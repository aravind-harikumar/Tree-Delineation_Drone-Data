def swap_columns(your_list, pos1, pos2):
    for item in your_list:
        item[pos1], item[pos2] = item[pos2], item[pos1]
