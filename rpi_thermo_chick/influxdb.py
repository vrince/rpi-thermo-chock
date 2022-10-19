
try:
    from influxdb_client import InfluxDBClient
    from influxdb_client.client.write_api import SYNCHRONOUS
except:
    pass

from rpi_thermo_chick import logger

client = None

def init_influxdb_client(config):
    global client
    try:
        client = InfluxDBClient(url=config.get('url', 'http://localhost:8086'), 
            token=config.get('token', ''), 
            org=config.get('org', 'org'))
        logger.warning(f'influxdb client created')
    except Exception as e:
        logger.info(f'cannot create influxdb client, exception({e})')


def write_to_influxdb(name='tempSensors', tags={}, fields={}, bucket='rpi_thermo_chick', org='org'):
    try:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        tags_flat = ',' + ','.join([f'{k}={v}' for k,v in tags.items()]) if tags else ''
        fields_flat = ','.join([f'{k}={v}' for k,v in fields.items()])
        write_api.write(bucket, org, f'{name}{tags_flat} {fields_flat}')
    except Exception as e:
        logger.warning(f'cannot write influxdb client, exception({e})')

def query_mean(name='tempSensors', field='inside', range='24h', window='15m', bucket='rpi_thermo_chick', org='org'):
    try:
        query_api = client.query_api()

        query = (f'from(bucket:"{bucket}")\n'
        f'|> range(start: -{range})\n'
        f'|> filter(fn:(r) => r._measurement == "{name}")\n'
        f'|> filter(fn: (r) => r["_field"] == "{field}")\n'
        f'|> aggregateWindow(every: {window}, fn: mean, createEmpty: false)\n'
        f'|> yield(name: "mean")')

        result = query_api.query(org=org, query=query)

        times = []
        records = []
        for table in result:
            for record in table.records:
                times.append(record.get_time().isoformat())
                records.append(record.get_value())

        return (times, records)

    except Exception as e:
        logger.warning(f'cannot write influxdb client, exception({e})')

