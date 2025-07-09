
def get_active_row_from_table(cursor, table_name, id):
    allowed_tables = {'items', 'categories', 'item_categories', 'orders'}
    if table_name.upper() not in (allowed_table.upper() for allowed_table in allowed_tables):
        raise ValueError(f"Invalid table name: {table_name}")
    
    query = f"SELECT id FROM {table_name} WHERE id = %s AND deleted = false;"
    cursor.execute(query, (id,))
    return cursor.fetchone()