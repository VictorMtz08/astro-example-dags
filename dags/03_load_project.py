from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models.connection import Connection
from time import time_ns
from datetime import datetime , timedelta
from airflow.utils.dates import days_ago
import os
from pymongo import MongoClient
from pandas import DataFrame
from google.cloud import bigquery
import pandas as pd

default_args = {
    'owner': 'Datapath',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def get_connect_mongo():

    CONNECTION_STRING ="mongodb+srv://atlas:T6.HYX68T8Wr6nT@cluster0.enioytp.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)

    return client


def start_process():
    print(" INICIO EL PROCESO!")

def end_process():
    print(" FIN DEL PROCESO!")



def load_products():
    print(f" INICIO LOAD PRODUCTS")
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["products"] 
    products = collection_name.find({})
    products_df = DataFrame(products)
    dbconnect.close()
    products_df['_id'] = products_df['_id'].astype(str)
    products_df['product_description'] = products_df['product_description'].astype(str)
    products_rows=len(products_df)
    print(f" Se obtuvo  {products_rows}  Filas")
    products_rows=len(products_df)
    if products_rows>0 :
        client = bigquery.Client(project='zeta-medley-405005')
        table_id =  "zeta-medley-405005.dep_raw.products"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("_id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("product_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("product_category_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("product_name", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("product_description", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("product_price", bigquery.enums.SqlTypeNames.FLOAT),
                bigquery.SchemaField("product_image", bigquery.enums.SqlTypeNames.STRING),
            ],
            write_disposition="WRITE_TRUNCATE",
        )


        job = client.load_table_from_dataframe(
            products_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla productos')




def transform_date(text):
    text = str(text)
    d = text[0:10]
    return d


def load_orders():
    print(f" INICIO LOAD ORDERS")
    
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["orders"] 
    orders = collection_name.find({})
    orders_df = DataFrame(orders)
    dbconnect.close()
    orders_df['_id'] = orders_df['_id'].astype(str)
    orders_df['order_date']  = orders_df['order_date'].map(transform_date)
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'], format='%Y-%m-%d').dt.date
    orders_rows=len(orders_df)
    print(f" Se obtuvo  {orders_rows}  Filas")
    orders_rows=len(orders_df)
    if orders_rows>0 :
        client = bigquery.Client(project='zeta-medley-405005')
        table_id =  "zeta-medley-405005.dep_raw.orders"
        
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("_id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("order_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_date", bigquery.enums.SqlTypeNames.DATE),
                bigquery.SchemaField("order_customer_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_status", bigquery.enums.SqlTypeNames.STRING),
            ],
            write_disposition="WRITE_TRUNCATE",
        )
    
    
        job = client.load_table_from_dataframe(
            orders_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.
    
        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla orders')
        




def transform_date(text):
    text = str(text)
    d = text[0:10]
    return d



def load_order_items():
    print(f" INICIO LOAD ORDER ITEMS")
    
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["order_items"] 
    order_items = collection_name.find({})  
    order_items_df = DataFrame(order_items)
    dbconnect.close()

    order_items_df['_id'] = order_items_df['_id'].astype(str)
    order_items_df['order_date']  = order_items_df['order_date'].map(transform_date)
    order_items_df['order_date'] = pd.to_datetime(order_items_df['order_date'], format='%Y-%m-%d').dt.date
    
    order_items_rows=len(order_items_df)
    print(f" Se obtuvo  {order_items_rows}  Filas")
    
    order_items_rows=len(order_items_df)
    if order_items_rows>0 :
        client = bigquery.Client(project='zeta-medley-405005')
        table_id =  "zeta-medley-405005.dep_raw.order_items"
        
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("_id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("order_date", bigquery.enums.SqlTypeNames.DATE),
                bigquery.SchemaField("order_item_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_order_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_product_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_quantity", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_subtotal", bigquery.enums.SqlTypeNames.FLOAT),
                bigquery.SchemaField("order_item_product_price", bigquery.enums.SqlTypeNames.FLOAT),
            ],
            write_disposition="WRITE_TRUNCATE",
        )
    
    
        job = client.load_table_from_dataframe(
            order_items_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.
    
        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla order_items')



def load_customers():
    print(f" INICIO LOAD CUSTOMERS")
    
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["customers"] 
    customers = collection_name.find({})
    customers_df = DataFrame(customers)
    dbconnect.close()

    customers_df['_id'] = customers_df['_id'].astype(str)
    
    customers_rows=len(customers_df)
    print(f" Se obtuvo  {customers_rows}  Filas")
    
    customers_rows=len(customers_df)
    
    if customers_rows>0 :
        client = bigquery.Client(project='zeta-medley-405005')
        table_id =  "zeta-medley-405005.dep_raw.customers"
        
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("_id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("customer_fname", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_lname", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_email", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_password", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_street", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_city", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_state", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_zipcode", bigquery.enums.SqlTypeNames.INTEGER),
            ],
            write_disposition="WRITE_TRUNCATE",
        )
    
    
        job = client.load_table_from_dataframe(
            customers_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.
    
        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla customers')



def load_categories():
    print(f" INICIO LOAD CATEGORIES")
    
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["categories"] 
    categories = collection_name.find({})
    categories_df = DataFrame(categories)
    dbconnect.close()
    
    categories_df = categories_df.drop(columns=['_id'])
    
    categories_rows=len(categories_df)
    print(f" Se obtuvo  {categories_rows}  Filas")
    
    categories_rows=len(categories_df)
    
    if categories_rows>0 :
        client = bigquery.Client(project='zeta-medley-405005')
        table_id =  "zeta-medley-405005.dep_raw.categories"
        
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("category_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("category_department_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("category_name", bigquery.enums.SqlTypeNames.STRING),
            ],
            write_disposition="WRITE_TRUNCATE",
        )
    
    
        job = client.load_table_from_dataframe(
            categories_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.
    
        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla categories')


def load_departments():
    print(f" INICIO LOAD DEPARTMENTS")
    
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["departments"] 
    departments = collection_name.find({})
    departments_df = DataFrame(departments)
    dbconnect.close()
    
    departments_df = departments_df.drop(columns=['_id'])
    
    departments_rows=len(departments_df)
    print(f" Se obtuvo  {departments_rows}  Filas")

    departments_rows=len(departments_df)
    
    if departments_rows>0 :
        client = bigquery.Client(project='zeta-medley-405005')
        table_id =  "zeta-medley-405005.dep_raw.departments"
        
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("department_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("department_name", bigquery.enums.SqlTypeNames.STRING)
            ],
            write_disposition="WRITE_TRUNCATE",
        )
    
    
        job = client.load_table_from_dataframe(
            departments_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.
    
        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla departments')


def load_departments_delta():
    print(f" DEPARTMENTS SOLO EJECUTA DIA LUNES")

def run_departments():
    today = date.today()
    if today.weekday()==1 :
        return "load_departments"
    else :
        return "load_departments_delta"



def get_group_status(text):
    text = str(text)
    if text =='CLOSED':
        d='END'
    elif text =='COMPLETE':
        d='END'
    else :
        d='TRANSIT'
    return d


def get_national_currency(amount):
    headers_filter = {
    'tipocambio': ['fecha' ,'compra','venta','nan']
    }
    
    dwn_url_tipocambio= 'https://www.sunat.gob.pe/a/txt/tipoCambio.txt'
    df = pd.read_csv(dwn_url_tipocambio, names=headers_filter['tipocambio'],sep='|')
    list_t= df.values.tolist()
    
    var1 = list_t[0][1]
    
    return amount * var1
    

def load_master_order():
    print(f" INICIO LOAD MASTER")    
    client = bigquery.Client(project='zeta-medley-405005')
    
    sql = """
        SELECT *
        FROM `zeta-medley-405005.dep_raw.order_items`
    """
    
    m_order_items_df = client.query(sql).to_dataframe()
    
    sql_2 = """
    SELECT *
    FROM `zeta-medley-405005.dep_raw.orders`
    """
    
    m_orders_df = client.query(sql_2).to_dataframe()
    
    df_join = m_orders_df.merge(m_order_items_df, left_on='order_id', right_on='order_item_order_id', how='inner')
    
    df_master=df_join[[ 'order_id', 'order_date_x', 'order_customer_id',
       'order_status',  'order_item_id',
       'order_item_order_id', 'order_item_product_id', 'order_item_quantity',
       'order_item_subtotal', 'order_item_product_price']]
    
    df_master=df_master.rename(columns={"order_date_x":"order_date"})
    
    df_master['order_status_group']  = df_master['order_status'].map(get_group_status)
    df_master['order_date'] = df_master['order_date'].astype(str)
    df_master['order_date'] = pd.to_datetime(df_master['order_date'], format='%Y-%m-%d').dt.date
    df_master['order_item_subtotal_mn']  = df_master['order_item_subtotal'].map(get_national_currency)

    master_rows=len(df_master)
    print(f" Se obtuvo  {master_rows}  Filas")

    df_master_rows=len(df_master)
    
    if df_master_rows>0 :
        client = bigquery.Client()
    
        table_id =  "zeta-medley-405005.dep_raw.master_order"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("order_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_date", bigquery.enums.SqlTypeNames.DATE),
                bigquery.SchemaField("order_customer_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_status", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("order_item_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_order_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_product_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_quantity", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_subtotal", bigquery.enums.SqlTypeNames.FLOAT),
                bigquery.SchemaField("order_item_product_price", bigquery.enums.SqlTypeNames.FLOAT),
                bigquery.SchemaField("order_status_group", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("order_item_subtotal_mn", bigquery.enums.SqlTypeNames.FLOAT),
            ],
            write_disposition="WRITE_TRUNCATE",
        )
    
    
        job = client.load_table_from_dataframe(
            df_master, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.
    
        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla master_order')
        


def load_bi_orders():
    print(f" INICIO LOAD BI_ORDERS")

    client = bigquery.Client(project='zeta-medley-405005')
    
    query_string = """
    create or replace table `zeta-medley-405005.dep_raw.bi_orders` as
    SELECT 
     order_date,c.category_name ,d.department_name 
     , sum (a.order_item_subtotal) order_item_subtotal
     , sum (a.order_item_quantity) order_item_quantity
    FROM `zeta-medley-405005.dep_raw.master_order` a
    inner join  `zeta-medley-405005.dep_raw.products` b on
    a.order_item_product_id=b.product_id
    inner join `zeta-medley-405005.dep_raw.categories` c on
    b.product_category_id=c.category_id
    inner join `zeta-medley-405005.dep_raw.departments` d on
    c.category_department_id=d.department_id
    group by order_date,c.category_name ,d.department_name
    """

    query_job = client.query(query_string)
    rows = list(query_job.result())
    print(f" Se obtuvo  {rows}  Filas")



def load_segment_customer():
    print(f" INICIO LOAD SEGMENT_CUSTOMER")

    client = bigquery.Client(project='zeta-medley-405005')
    
    query_string = """
    create or replace table `zeta-medley-405005.dep_raw.segment_customer` as
    select customer_id,category_name , order_item_subtotal from
    (
      SELECT customer_id,category_name,order_item_subtotal,
      RANK() OVER (PARTITION BY customer_id ORDER BY order_item_subtotal DESC) AS rank_ 
     FROM (
          SELECT 
          d.customer_id ,c.category_name 
          , sum (a.order_item_subtotal) order_item_subtotal
          FROM `zeta-medley-405005.dep_raw.master_order` a
          inner join  `zeta-medley-405005-410714.dep_raw.products` b on
          a.order_item_product_id=b.product_id
          inner join `zeta-medley-405005.dep_raw.categories` c on
          b.product_category_id=c.category_id
          inner join `zeta-medley-405005.dep_raw.customers` d on
          a.order_customer_id=d.customer_id
          group by 1,2
      )
    )
    where rank_=1
    """

    query_job = client.query(query_string)
    rows = list(query_job.result())
    print(f" Se obtuvo  {rows}  Filas")



def load_segmentToMongo():
    print(f" INICIO LOAD SEGMENT_CUSTOMER")

    client = bigquery.Client(project='zeta-medley-405005')
    
    query_string = """
    select customer_id ,category_name ,order_item_subtotal
    from `zeta-medley-405005.dep_raw.segment_customer`
    """
    
    segment_df = client.query(query_string).to_dataframe()
    segment_dict = segment_df.to_dict(orients = 'records')
    
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["segment_VictorMartinez"] 
    collection_name.insert_many(segment_dict)
    dbconnect.close()




with DAG(
    dag_id="load_project",
    schedule="20 04 * * *", 
    start_date=days_ago(2), 
    default_args=default_args
) as dag:
    step_start = PythonOperator(
        task_id='step_start_id',
        python_callable=start_process,
        dag=dag
    )
    step_load_products = PythonOperator(
        task_id='load_products_id',
        python_callable=load_products,
        dag=dag
    )
    step_load_orders = PythonOperator(
        task_id='load_orders_id',
        python_callable=load_orders,
        dag=dag
    )
    step_load_order_items = PythonOperator(
        task_id='load_order_items_id',
        python_callable=load_order_items,
        dag=dag
    )
    step_load_customers = PythonOperator(
        task_id='load_customers_id',
        python_callable=load_customers,
        dag=dag
    )
    step_load_categories = PythonOperator(
        task_id='load_categories_id',
        python_callable=load_categories,
        dag=dag
    )
    step_load_departments = PythonOperator(
        task_id='load_departments_id',
        #python_callable=load_departments,
        python_callable=run_departments,
        dag=dag
    )
    step_load_master_order = PythonOperator(
        task_id='load_master_order_id',
        python_callable=load_master_order,
        dag=dag
    )
    step_load_bi_orders = PythonOperator(
        task_id='load_bi_orders_id',
        python_callable=load_bi_orders,
        dag=dag
    )
    step_load_segment_customer = PythonOperator(
        task_id='load_segment_customer_id',
        python_callable=load_segment_customer,
        dag=dag
    )
    step_load_segmentToMongo= PythonOperator(
        task_id='load_segmentToMongo_id',
        python_callable=load_segmentToMongo,
        dag=dag
    )
    step_end = PythonOperator(
        task_id='step_end_id',
        python_callable=end_process,
        dag=dag
    )
    step_start>>step_load_products
    step_start>>step_load_orders
    step_start>>step_load_order_items
    step_start>>step_load_customers
    step_start>>step_load_categories
    step_start>>step_load_departments
    step_load_products>>step_load_master_order
    step_load_orders>>step_load_master_order
    step_load_order_items>>step_load_master_order
    step_load_customers>>step_load_master_order
    step_load_categories>>step_load_master_order
    step_load_departments>>step_load_master_order
    step_load_master_order>>step_load_bi_orders>>step_load_segment_customer>>step_load_segmentToMongo>>step_end

