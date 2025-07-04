from unittest.mock import MagicMock

def setup_mock_db(
    mock_get_db_connection,
    fetchone = None,
    fetchall = None,
    side_effect = None,
    description= None,
):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = fetchone
    mock_cursor.fetchall.return_value = fetchall
    mock_cursor.description = description
    
    if side_effect is not None:
        mock_cursor.fetchone.side_effect = side_effect
        mock_cursor.fetchall.side_effect = side_effect
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    