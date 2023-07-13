# Utiltity to analyze naming consistency in Python project

Utitly shows similar names in grouuped manner, with code line contains it.

It is intended to detect if names really describe what's inside (to avoid cases where 'file' is path in one context, file content in other one, and custom object in third)
Also, it could detect redundant variety in name clauses, like 'function_param', 'fn_obj', 'func_name', 'f_body' 
