
label = "this.that.thing"


def split_label_path(path):
    split_path = path.split('.')
    return split_path, len(split_path)


print(split_label_path(label))
split_path, num_splits = split_label_path(label)
res = {'this': {'the': "quick", "that": {"brown": "fox"}}}

data_to_insert = "some good stuff"


def resolve_dict_path(data, split_label, layers, results, layer=0):
    if layer == layers - 1:
        results[split_label[layer]] = data
        return results
    try:
        result = results[split_label[layer]]
    except KeyError:
        results[split_label[layer]] = {}
        result = results[split_label[layer]]
    results[split_label[layer]] = resolve_dict_path(data, split_label, layers, result, layer + 1)
    return results


a = resolve_dict_path(data_to_insert, split_path, num_splits, res)
print(a)
res = {}
a = resolve_dict_path(data_to_insert, split_path, num_splits, res)
print(a)
