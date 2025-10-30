import traceback, inspect


def log_stack():
	stack_list = traceback.extract_stack()
	# stack_list is a list of FrameSummary objects
	for frame in stack_list:
		print(f"File: {frame.filename}, Line: {frame.lineno}, Function: {frame.name}")

def log_all_frame_locals():
	# 1. Get the list of frame records, which includes the live frame object
	# The [1:] skips the current frame (log_all_frame_locals) itself
	stack = inspect.stack()[1:] 

	print("--- CALL STACK LOCALS ---")
	
	for frame_record in stack:
		# frame_record.frame is the actual live frame object
		frame = frame_record.frame 
		
		# Get the locals dictionary from the frame
		frame_locals = frame.f_locals 

		# Get static info for display
		filename = frame_record.filename
		lineno = frame_record.lineno
		function_name = frame_record.function
		if filename!=r"C:\Users\iftak\Desktop\projects\riviagw\data_filter_query\queryparser.py" or function_name not in ['parse_field_spec', '__consume_chars'] :
			continue

		print(f"\n[{filename}:{lineno}] - Function: {function_name}")
		print("-" * 30)
		# Print all locals for this frame
		if frame_locals:
			for name, value in frame_locals.items():
				# Use repr() for a clear string representation of the value
				print(f"  {name}: {repr(value)}")
		else:
			print("  (No local variables)")

		# IMPORTANT: Delete the reference to the frame to avoid reference cycles
		# This is critical for preventing memory leaks
		del frame
		
	print("\n--- END STACK LOCALS ---")

