#!/usr/bin/env python3
import sys
import os
import timechange

def query_columns(data_columns):
    answer = ""
    print("Should we use all columns? (yes/no): ")
    answer = input().rstrip()
    while answer not in ("yes", "no"):
        print("Invalid answer")
        print("Should we use all columns? (yes/no): ")
        answer = input().rstrip()
    if answer == "no":
        print("What columns should be removed?")
        print("(enter a comma separated list of column names): ")
        answer = input().rstrip().split(',')
        while True:
            backup_columns = data_columns
            try:
                for column in answer:
                    data_columns.remove(column)
                break
            except Exception as e:
                data_columns = backup_columns
                print("Invalid answer. Perhaps you gave an index number not a column header name.")
                print("What columns should be removed?")
                print("(enter a comma separated list of column numbers): ")
                answer = input().rstrip().split(',')
        print("The data now will only use these columns:")
        for index, col_name in enumerate(data_columns):
            print("{}: {}".format(index, col_name))
    return data_columns

tc = timechange.TimeChange()
if len(sys.argv) < 2:
    print("Need a directory (not an individual .csv)")
    exit()

input_directory = sys.argv[1]
print("Found the following files in %s" % input_directory)
print(str(os.listdir(input_directory)))

individual_strip = True
group_stripped_columns = []
headersList = []
for file_id, csv_filename in enumerate(os.listdir(input_directory)):
    csv_filename = os.path.join(sys.argv[1], csv_filename)
    data_columns = list(tc.get_csv_columns(csv_filename))
    headersList += [data_columns]

if all(headers==headersList[0] for headers in headersList):
    print("Headers identical in all files.")
    print("Do you want to strip columns for each file individually?")
    answer = ""
    answer = input().rstrip()
    while answer not in ("yes", "no"):
        print("Invalid answer")
        print("Should we use all columns? (yes/no): ")
        answer = input().rstrip()
    if answer == "no":
        individual_strip = False
        group_strip_columns = query_columns(data_columns)

for file_id, csv_filename in enumerate(os.listdir(input_directory)):
    print(csv_filename)
    csv_filename = os.path.join(sys.argv[1], csv_filename)
    data_columns = list(tc.get_csv_columns(csv_filename))
    print("Found {} columns".format(len(data_columns)))
    for index, col_name in enumerate(data_columns):
        print("{}: {}".format(index, col_name))

    if individual_strip:
        data_columns = query_columns(data_columns)
    else:
        data_columns = group_strip_columns

    data = tc.read_csv(csv_filename, usecols=data_columns)

    if not os.path.isdir("data"):
        os.mkdir("data")
    if not os.path.isdir("data/results"):
        os.mkdir("data/results")

    from PIL import Image
    features = tc.extract_features(data, data_size=1000)
    img = Image.fromarray(255*features, 'L')
    img.save("data/results/test{}.png".format(file_id))
