import MySQLdb
from MySQLdb.cursors import DictCursor
import argparse


def generate_script(conn, *, database, collation, charset):
	env = dict(database=database, collation=collation, charset=charset)

	with conn.cursor() as c:
		c.execute('SELECT * FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s', [database])
		db = c.fetchone()
		if db['DEFAULT_COLLATION_NAME'] != collation or db['DEFAULT_CHARACTER_SET_NAME'] != charset:
			yield 'ALTER DATABASE {database} CHARACTER SET = {charset} COLLATE = {collation}'.format_map(env)
		
		c.execute('SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_TYPE="BASE TABLE"', [database])
		for table in c:
			if table['TABLE_COLLATION'] != collation:
				t_env = dict(env, **table)
				yield 'ALTER TABLE {TABLE_NAME} CONVERT TO CHARACTER SET {charset} COLLATE {collation}'.format_map(t_env)


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('-H', '--host', default='localhost')
	ap.add_argument('-u', '--user', default='root')
	ap.add_argument('-p', '--password', default='')
	ap.add_argument('-d', '--database', required=True)
	ap.add_argument('--charset')
	ap.add_argument('-c', '--collation', default='utf8mb4_unicode_ci')
	ap.add_argument('-x', '--execute', action='store_true')
	args = ap.parse_args()

	if not args.charset:
		args.charset = args.collation.split('_')[0]

	if not args.collation.startswith(args.charset):
		raise ValueError('Collation and charset mismatch!')

	conn = MySQLdb.connect(
		host=args.host,
		user=args.user,
		password=args.password,
		cursorclass=DictCursor,
	)
	conversion_sql = generate_script(
		conn,
		database=args.database,
		collation=args.collation,
		charset=args.charset,
	)

	with conn.cursor() as c:
		if args.execute:
			c.execute('USE {}'.format(args.database))
		for statement in conversion_sql:
			print('{};'.format(statement))
			if args.execute:
				c.execute(statement)


if __name__ == '__main__':
	main()
