
# Initializing dictionaries and lists required for computation
Candidate_Dict = {}
MIS_Dict_eachitem = {}
MIS_ip_Extract = {}
SortedMIS_Dict_eachitem = {}
Item_Count = {}
Frequent_itemList = list([] for _ in range(10))
Candidate_List = list([] for _ in range(10))
SDC_Value = 0.0
Item_List = []
Transaction_List = []
TotalNum_transactions = 0
L = []


# Reading param file, transaction files
def readInput_Files():
    global TotalNum_transactions, Item_List, Item_Count, SDC_Value, Transaction_List, rest_value, MIS_Dict_eachitem
    # transaction_file_path = "data-1.txt"
    transaction_file_path = "data-2.txt"
    transaction_file = open(transaction_file_path, encoding = 'utf-8-sig')
    # transaction_file = pd.read_csv(transaction_file_path, fileEncoding = "UTF-8-BOM")
    for i in transaction_file:
        Transaction_List.append([])
        transaction = i.replace(' ', '').replace('{', '').replace('}', '').split(',')

        #append all individual transaction as a list to another list eg : [[10,20],[30,70,80]]
        for t in transaction:
            Transaction_List[len(Transaction_List) - 1].append(int(t))
    # print("Transaction_List", Transaction_List)
    TotalNum_transactions = len(Transaction_List)
    # print("TotalNum_transactions", TotalNum_transactions)

    #intitalize each item of the transaction list to 0; eg: MIS_Dict_eachitem - {40:0, 50:0 ,.....}
    # print("MIS_Dict_eachitem BEFORE ", MIS_Dict_eachitem)
    for i in Transaction_List:
        for j in i:
            if j not in MIS_Dict_eachitem.keys():
                MIS_Dict_eachitem[j] = 0


    # MIS_filepath = "para-1.txt"
    MIS_filepath = "para-2.txt"
    MIS_file = open(MIS_filepath)

    for i in MIS_file:
        if i.find('SDC') != -1:
            SDC_Value = float(i.replace(' ', '').rstrip().split('=')[1])

        if i.find('MIS') != -1:
            MIS_ip_Extract = i.replace(' ', '').replace('MIS', '').replace('(', '').replace(')', '').rstrip().split('=')

            if MIS_ip_Extract[0] != "rest" and int(MIS_ip_Extract[0]) in MIS_Dict_eachitem.keys():
                MIS_Dict_eachitem[int(MIS_ip_Extract[0])] = float(MIS_ip_Extract[1])
            else:
                rest_value = float(MIS_ip_Extract[1])


    #fill the remaining MIS with the rest value

    for key, value in MIS_Dict_eachitem.items():
        if value == 0:
            MIS_Dict_eachitem[key] = rest_value

    unique_items = sorted(MIS_Dict_eachitem, key=MIS_Dict_eachitem.__getitem__)
    for item in unique_items:
        Item_List.append(int(item))
        Item_Count[int(item)] = 0

    for i in Transaction_List:
        for j in i:
            if j not in Item_Count.keys():
                Item_Count[j] = 0
            else:
                Item_Count[j] = Item_Count[j] + 1


# initial pass
def init_Pass():
    global L
    for i in range(len(Item_List)):
        if i != 0:
            if ((Item_Count.get(Item_List[i]) / TotalNum_transactions) >= MIS_Dict_eachitem.get(Item_List[0])):
                L.append(Item_List[i])
        else:
            L.append(Item_List[0])

    #soritng L and assigning index to it so that we get the increasing order for choosing from L
    for i in range(len(L)):
        SortedMIS_Dict_eachitem[L[i]] = i


# Adding 1-Itemsets to the Frequent_itemList
def Frequent_item1():
    global Frequent_itemList
    if Frequent_itemList[1] is not None:
        for i in range(len(L)):
            if (Item_Count.get(L[i]) / TotalNum_transactions) >= MIS_Dict_eachitem.get(L[i]):
                Frequent_itemList[1].append([L[i]])
    # print("Frequent_itemList after", Frequent_itemList)


# Adding i-Itemsets to the Frequent_itemList
def Frequent_item_i():
    level = 2
    global Frequent_itemList, Candidate_Dict
    while 1:
        if not Frequent_itemList[level - 1]:
            break

        if level == 2:
            generate_level2_Candidate()
        else:
            generate_level_i_Candidate(level)

        for transac in Transaction_List:
            for cand in Candidate_List[level]:
                if set(cand).issubset(set(transac)):
                    if Candidate_Dict.get(tuple(cand)) != None:
                        Candidate_Dict[tuple(cand)] += 1
                    else:
                        Candidate_Dict[tuple(cand)] = 1

        for cand in Candidate_List[level]:
            if Candidate_Dict.get(tuple(cand)) != None:
                if Candidate_Dict.get(tuple(cand)) / TotalNum_transactions >= MIS_Dict_eachitem[cand[0]]:
                    Frequent_itemList[level].append(cand[:])
        level += 1


# Generating candidates for Level 2 which works differently as compared to other levels
def generate_level2_Candidate():
    global Candidate_List, L
    for item_in_L in range(0, len(L)):
        if (Item_Count[L[item_in_L]] / TotalNum_transactions) >= MIS_Dict_eachitem[L[item_in_L]]:
            for data in range(item_in_L + 1, len(L)):
                if (abs((Item_Count[L[data]] / TotalNum_transactions) - (Item_Count[L[item_in_L]] / TotalNum_transactions)) <= SDC_Value) and (Item_Count[L[data]] / TotalNum_transactions) >= MIS_Dict_eachitem[L[item_in_L]]:
                    Candidate_List[2].append([])
                    Candidate_List[2][len(Candidate_List[2]) - 1].append(L[item_in_L])
                    Candidate_List[2][len(Candidate_List[2]) - 1].append(L[data])
    Candidate_List[2].sort(key=lambda row: row[1])


def generate_level_i_Candidate(num):
    element = 0
    freq_level = num - 1
    for i in range(0, len(Frequent_itemList[freq_level])):
        for j in range(0, len(Frequent_itemList[freq_level])):
            while (element < freq_level - 1) and (Frequent_itemList[freq_level][i][element] == Frequent_itemList[freq_level][j][element]):
                element += 1

            if element == freq_level - 1:
                if ((SortedMIS_Dict_eachitem[Frequent_itemList[freq_level][i][element]] < SortedMIS_Dict_eachitem[Frequent_itemList[freq_level][j][element]]) and (
                        abs((Item_Count[Frequent_itemList[freq_level][i][element]] / TotalNum_transactions) - (Item_Count[Frequent_itemList[freq_level][j][element]] / TotalNum_transactions)) <= SDC_Value)):
                    Candidate_List[freq_level + 1].append(list(Frequent_itemList[freq_level][i]))
                    Candidate_List[freq_level + 1][len(Candidate_List[freq_level + 1]) - 1].append(Frequent_itemList[freq_level][j][element])

            element = 0


def result():
    global Item_Count, Frequent_itemList
    Frequent_itemList = [x for x in Frequent_itemList if x != []]
    # print("FREQUENT_ITEM", Frequent_itemList)
    # result_path = "1_1_result.txt"
    result_path = "1_2_result.txt"
    output_file = open(result_path, "w")

    count = 0
    for _ in Frequent_itemList[0]:
        count += 1
    output_file.write("(63\n\n(Length-1 " + str(count) + "\n\n")
    if Frequent_itemList != []:
        for t in Frequent_itemList[0]:
            count += 1
            output_file.write('\t' + '(' + str(t[0]) + ')\n\n')
    output_file.write(")\n")

    for i in range(1, len(Frequent_itemList)):
        total_count = 0
        for _ in Frequent_itemList[i]:
            total_count += 1
        output_file.write('\n(Length-'+ str(i + 1) + " "+str(total_count)+"\n\n")
        count = 0
        for t in Frequent_itemList[i]:
            total_cnt = 0
            for j in range(len(Transaction_List)):
                if set(Transaction_List[j]) >= set(t):
                    total_cnt = total_cnt + 1
            count += 1
            output_file.write('\t' + '(' + str(t).replace("[", "").replace("]", "").replace(",", "") + ')\n\n')
        output_file.write(")\n")
    output_file.write("\n)")


def main():
    readInput_Files()
    init_Pass()
    Frequent_item1()
    Frequent_item_i()
    result()
    print("Output generated in result.txt")


if __name__ == "__main__":
    main()
