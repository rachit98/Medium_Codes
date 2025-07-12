import csv
def are_csvs_equal(csv_path1, csv_path2):
    """
    Returns True if two CSV files have the exact same content (row-by-row and cell-by-cell).
    Ignores differences in line endings and trailing whitespace.
    """
    with open(csv_path1, newline='', encoding='utf-8') as f1, \
         open(csv_path2, newline='', encoding='utf-8') as f2:
        reader1 = csv.reader(f1)
        reader2 = csv.reader(f2)
        for row1, row2 in zip(reader1, reader2):
            # Strip whitespace from each cell for robust comparison
            if [cell.strip() for cell in row1] != [cell.strip() for cell in row2]:
                print("Different")
                return False
        # Check for extra rows in either file
        try:
            next(reader1)
            return False
        except StopIteration:
            pass
        try:
            next(reader2)
            return False
        except StopIteration:
            pass
    print("Files are same")
    return True

print(are_csvs_equal('./csv/input.csv', './csv/output.csv'))