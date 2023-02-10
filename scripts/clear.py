from rich.pretty import pprint
import rich.prompt

from resolution.database.client import get_client

def run():
    print('Removing all databases and collections from MongoDB', flush=True)
    if rich.prompt.Confirm.ask('Are you absolutely sure you want to continue?'):
        raise NotImplementedError('Not implemented to prevent mistakes! Re-enable here if you truly want to delete the entire database')
        # client = get_client('mongo_credentials.json', local=True)
        # for database_name in client.list_database_names():
        #     if database_name not in {'jstor_database', 'admin', 'validation'}:
        #         if rich.prompt.Confirm.ask(f'Drop database {database_name}'):
        #             client.drop_database(database_name)

