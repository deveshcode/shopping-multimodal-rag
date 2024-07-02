
import pandas as pd
import boto3
from io import StringIO
from data_pipeline import combined_df


def upload_s3(df,i):
    s3 = boto3.client("s3",aws_access_key_id="",aws_secret_access_key="")
    csv_buf = StringIO()
    df.to_csv(csv_buf, header=True, index=False)
    csv_buf.seek(0)    
    s3.put_object(Bucket="leloballe", Body=csv_buf.getvalue(), Key=i)

upload_s3(combined_df,"nike_mens_clothing_with_additional_data.csv")