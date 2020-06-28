from utils import load_json_file, save_json_file


class JSONDatabase:

    def __init__(self, file_name):
        self.file_name = file_name
        rows = load_json_file(file_name)

        # the json must be a list
        if not isinstance(rows, list):
            raise ValueError("To serve as a database, the JSON data should be stored as a list!")

        # all values must be dicts
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"All row values much be dictionaries! Found: {row}")

        # mapping of row index to values
        self.row_map = {row.get("_id"):row for row in rows}
        
        # precalculate the next available row for inserting
        self.next_open_row = None
        row_index = 0
        while self.next_open_row is None:
            if row_index not in self.row_map:
                self.next_open_row = row_index
            row_index += 1
    

    def get_all(self):
        return list(self.row_map.values())


    def query_all(self, query_params):
        matches = []
        for obj in self.row_map.values():
            for query_k, query_v in query_params.items():
                if (obj.get(query_k) or "").lower() == (query_v or "").lower():
                    matches.append(obj)
        return matches


    def save(self):
        save_json_file(self.get_all(), self.file_name)


    def insert(self, data):
        data["_id"] = self.next_open_row
        self.next_open_row += 1
        self.row_map[data["_id"]] = data
        self.save()
    

    def update(self, row_index_or_object, data):
        # no changing row index using the update method
        if "_id" in data:
            raise ValueError(f"Cannot change the row index using update!")

        row_index = self._get_row_index(row_index_or_object)

        # if there is already data for that row, then update it
        # else just set the value to the given value
        entry = self.row_map.get(row_index, None)
        if entry:
            for k, v in data.items():
                entry[k] = v
        else:
            entry = data
        self.save()


    def _get_row_index(self, row_index_or_object):
        # get the row index if the object is a dictionary
        # else just take it as it is
        if isinstance(row_index_or_object, dict):
            row_index = row_index_or_object.get("_id")
            if row_index is None:
                raise ValueError(f"The given object {row_index_or_object} does not have an _id field.")
            return row_index
        elif isinstance(row_index_or_object, int):
            return row_index_or_object
        else:
            raise ValueError(f"Given unsupported row type: {type(row_index_or_object)}")


    def remove(self, row_index_or_object):
        row_index = self._get_row_index(row_index_or_object)
        
        # delete data in that row
        del self.row_map[row_index]

        # update next open row if you deleted the previously open row
        if row_index == self.next_open_row - 1:
            self.next_open_row = row_index

        self.save()
