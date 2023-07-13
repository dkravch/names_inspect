# Utiltity to analyze naming consistency in Python project

Utitly shows similar names in grouuped manner, with code line contains it.

It is intended to detect if names really describe what's inside (to avoid cases where _file_ is path in one context, file content in other one, and custom object in third).

Also, it could detect redundant variety in name clauses, like _function_param_, _fn_obj_, _func_name_, _f_body_. 
