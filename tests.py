#!/usr/bin/env python3
import sys
import os
import timechange

tc = timechange.TimeChange()
if len(sys.argv) < 2:
    print("Need a directory (not an individual .csv)")
    exit()
for file_id, csv_filename in enumerate(os.listdir(sys.argv[1])):
    print(csv_filename)
    csv_filename = os.path.join(sys.argv[1], csv_filename)
    data_columns = list(tc.get_csv_columns(csv_filename))
    print("Found {} columns".format(len(data_columns)))
    for index, col_name in enumerate(data_columns):
        print("{}: {}".format(index, col_name))

    answer = ""
    print("Should we use all columns? (yes/no): ")
    answer = input().rstrip()
    while answer not in ("yes", "no"):
        print("Invalid answer")
        print("Should we use all columns? (yes/no): ")
        answer = input().rstrip()
    if answer == "no":
        print("What columns should be removed? (enter a comma separated list of column names): ")
        answer = input().rstrip().split(',')
        while True:
            backup_columns = data_columns
            try:
                for column in answer:
                    data_columns.remove(column)
                break
            except Exception as e:
                data_columns = backup_columns
                print("Invalid answer - perhaps you gave an index number not a column header name?")
                print("What columns should be removed? (enter a comma separated list of column numbers): ")
                answer = input().rstrip().split(',')
        print("The data now will only use these columns:")
        for index, col_name in enumerate(data_columns):
            print("{}: {}".format(index, col_name))

    data = tc.read_csv(csv_filename, usecols=data_columns)

    if not os.path.isdir("data"):
        os.mkdir("data")
    if not os.path.isdir("data/results"):
        os.mkdir("data/results")

    from PIL import Image
    features = tc.extract_features(data, data_size=1000)
    img = Image.fromarray(255*features, 'L')
    img.save("data/results/test{}.png".format(file_id))
