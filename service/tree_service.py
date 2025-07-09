from db.content_hierarchy_access import ContentHierarchyDataAccess

class TreeService:
    def __init__(self):
        pass

    def update_preset(self, tree_id, preset_id):
        with ContentHierarchyDataAccess() as cha:
            cha.update_data(child_id=tree_id,  preset_id = preset_id)

    def delete_preset(self, tree_id):
        with ContentHierarchyDataAccess() as cha:
            cha.delete_preset(child_id=tree_id)

    def get_preset_by_tree_id(self, id):
        with ContentHierarchyDataAccess() as cha:
            data = cha.get_data_by_child_id(id)
            if data:
                return data.preset_id

    def is_top_node(self, id):
        with ContentHierarchyDataAccess() as cha:
            data = cha.get_data_by_child_id(int(id))
            return data.parent_id is None

    def exist_preset(self, id):
        with ContentHierarchyDataAccess() as cha:
            data = cha.get_data_by_child_id(int(id))
            return data.preset_id is not None

    def get_name_by_tree_id(self, id):
        with ContentHierarchyDataAccess() as cha:
            data = cha.get_data_by_child_id(id)
            if data:
                return data.name