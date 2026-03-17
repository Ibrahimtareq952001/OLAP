import glob
import pandas as pd
import json
from avro.datafile import DataFileReader
from avro.io import DatumReader
import pyarrow as pa
import pyarrow.parquet as pq

def convert_folder_to_parquet(input_folder, output_file):
    files = glob.glob(f'{input_folder}/*')
    total = len(files)
    print(f"Processing {total} files from {input_folder}...")
    
    writer = None
    total_rows = 0
    
    for i, f in enumerate(files):
        records = []
        try:
            # Try Avro first
            with open(f, 'rb') as avro_file:
                reader = DataFileReader(avro_file, DatumReader())
                for record in reader:
                    records.append(record)
                reader.close()
        except Exception:
            try:
                with open(f, 'r') as json_file:
                    content = json_file.read().strip()
                    if content.startswith('['):
                        records = json.loads(content)
                    else:
                        for line in content.split('\n'):
                            if line.strip():
                                records.append(json.loads(line))
            except Exception:
                pass
        
        if records:
            df = pd.DataFrame(records)
            table = pa.Table.from_pandas(df)
            if writer is None:
                writer = pq.ParquetWriter(output_file, table.schema)
            writer.write_table(table)
            total_rows += len(records)
        
        if (i+1) % 50 == 0:
            print(f"  Processed {i+1}/{total} files, {total_rows} rows so far...")
    
    if writer:
        writer.close()
        print(f"✅ Saved {total_rows} rows to {output_file}")
    else:
        print(f"❌ No records found in {input_folder}")

convert_folder_to_parquet(
    '/Users/ibrahimtarek/nifi-output/dim_supplier',
    '/Users/ibrahimtarek/nifi-output/dim_supplier.parquet'
)
convert_folder_to_parquet(
    '/Users/ibrahimtarek/nifi-output/dim_customer',
    '/Users/ibrahimtarek/nifi-output/dim_customer.parquet'
)
convert_folder_to_parquet(
    '/Users/ibrahimtarek/nifi-output/fact_lineitem',
    '/Users/ibrahimtarek/nifi-output/fact_lineitem.parquet'
)
