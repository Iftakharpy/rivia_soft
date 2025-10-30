from pprint import pp
from queryparser import parse_and_build_q


queries = [
    '''name contains "an"''',
    '''name == "ad"''',
    '''name eq "ab"''',
    '''file_no = 2.100''',
    '''pk = 1''',
    '''pk is 1''',
    '''pk is not 1''',
    '''pk in [1, 2]''',
    '''pk in [1, 2] or name contains "ks"''',
    '''pk is -2 ''',
    '''pk in [1, 2] (pk in [3, 4])''',
    '''(pk in [1, 2]) (pk in [3, 4])''',
    '''pk in [1, 2] (pk in [3, 4])''',
    '''pk in [1, 2] (pk in [3, 4]) (pk in [7, 8])''',
    '''(pk in [1, 2]) (pk in [3, 4]) (pk in [7, 8])''',
	
    '''likes_count >= 500 or comments_count >= 50 and likes_count >= 500 or comments_count >= 50''',
	
	'''
	(updated_at >= 2020-02-01 and created_at <= 2020-02-29) 
	or 
	(modified_at >= 2020-01-01 and updated_at <= 2020-01-31)''',
	
	'''
	(field_name1 >= 2020-02-01 and field_name2 gte 32) 
	or 
	(modified_at >= 2020-01-01 and updated_at <= 2020-01-31)''',
	
	"""
(
	age>3 and rating<3 and
		(
			(
				updated_at >= 2020-02-01 or updated_at <= "2011-02-01"
			)
			and
			updated_at_69 <= "2020-02-29"#test
		)
	or
	(
		created_at >= 2020-01-01 and created_at <= 2020-01-31
	)
)""",
"""status is not None""",
"""status is not active""",
"""status eq active""",
"""status not active""",
"""status is 'active'""",
"""is_active == yes""",
"""status not 'ac\\\\"tive'""",
"""status is not active""",
"""status in {'active', 'hold', 'hold'}""",
"""status in ('active', 'hold', 'hold')""",


	# invalid
    '''pk in [1, 2] _and name contains "ks"''',
    '''pk in [1, 2] and_ name contains "ks"''',
    '''pk in [1, 2] and_ ''',
    '''pk in [1, 2] and ''',
    '''pk in [1, 2] pk in [3, 4]''',
    '''(pk in [1, 2]) pk in [3, 4]''',
    '''pk in [1, 2] )(pk in [3, 4])''',

	"""
(
	age>3 and rating<3 and
		(
			(
				updated_at >= 2020-02-01 or updated_at <= 2011-02-01
			)
			and 
			updated_at <= 2020-02-29
		) 
	or 
	(
		created_at >= 2020-01-01 and created_at <= 2020-01-31
	)
) or age<3 ))""",

	"""or( age>3 and rating<3 and (
				(updated_at >= 2020-02-01 or updated_at <= 2011-02-01)
					and 
				updated_at <= 2020-02-29
			) or 
		(created_at >= 2020-01-01 and created_at <= 2020-01-31))""",

	"""( age>3 and rating<3 and (
				(updated_at >= 2020-02-01 or updated_at <= 2011-02-01)
					and 
				updated_at <= 2020-02-29
			) or 
		(created_at >= 2020-01-01 and created_at !<= 2020-01-31)) and""",
]

if __name__=="__main__":
	# run_test_cases(field_spec_parser_test_cases)
	for idx, query in enumerate(queries):
		result = parse_and_build_q(None, query)
		print("-"*75)
		pp(f"Query {idx:02}: {query}")
		pp(result)
		print("-"*75)
		print()
		print()
	