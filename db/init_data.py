from db.content_hierarchy_access import ContentHierarchyDataAccess

def insert_default_content_hierarchy():
    with ContentHierarchyDataAccess() as chda:
        try:
            exist = chda.has_data()
            if not exist:
                chda.insert_data(None, 0, "root", 0)
                print("insert default data")
            else:
                pass
        except Exception as e:
            print("insert default data error", e)