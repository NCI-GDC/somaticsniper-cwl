import postgres
import argparse

if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="Variant calling using Somatic-Sniper")

    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--config", default=None, help="path to config file", required=True)
    args = parser.parse_args()

    s = open(args.config, 'r').read()
    config = eval(s)

    DATABASE = {
        'drivername': 'postgres',
        'host' : 'pgreadwrite.osdc.io',
        'port' : '5432',
        'username': config['username'],
        'password' : config['password'],
        'database' : 'prod_bioinfo'
    }
    engine = postgres.db_connect(DATABASE)
    (tumor, tumor_file, normal, normal_file) = postgres.get_complete_cases(engine)

    for case_id in tumor:
        for tum in tumor[case_id]:
            for norm in normal[case_id]:
                pair = [norm, tum]
                print case_id, pair
                postgres.add_status(engine, case_id, pair, "TBD", "unknown")
