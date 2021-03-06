# -*- coding: utf-8 -*-
import MeCab
import re

def DoNLP(rawData, targetTag=None, mode=None):
    if mode == None:
        mode = 'Word'

    words = rawData.split(' ')
    for word in words:
        if word.__contains__('@') or word.__contains__('http'):
            words.remove(word)

    rawData = ''
    for word in words:
        rawData = rawData + word + ' '

    for symbal in ['"', "'", '(', ')']:
        rawData = rawData.replace(symbal, ',')

    pattern = ",\s+?,+"
    repl = ','
    rawData = re.sub(pattern=pattern, repl=repl, string=rawData)

    exceptTag = ['NNB', 'VCP', 'VCN', 'XSN', 'XSV', 'XSA', 'MAG', 'MAJ', 'IC', 'JKS',
                    'JKC', 'JKG', 'JKO', 'JKB', 'JKM', 'JKI', 'JKQ', 'JC', 'JX', 'ETM', 'ETN', 
                    'EP', 'EF', 'EC', 'VX', 'SC', 'SF', 'SE', 'SSO', 'SSC', 'SY', 'SN', 'UNKNOWN']
    connectTag = ['NNP', 'SL', 'SN', 'SY']
    if mode == 'Review':
        connectTag.append('NNG')
    exceptSymbal = ['.', '+']
    resultString = []
    tagedData = MeCab.Tagger().parse(rawData)

    resultData = tagedData.split('\n')
    dataList = []

    for data in resultData:
        dataSet = []
        splitData = data.split('\t')
        if len(splitData) == 2:
            word = splitData[0]
            tagDetail = splitData[1].split(',')
        else:
            continue
        
        tag = tagDetail[0]
        tagType = tagDetail[4]
        firstTag = tagDetail[5]
        expression = tagDetail[7]

        if tag == 'MAG':
            if tagDetail[1] == '*':
                tag = 'UNKNOWN'
            else:
                MAGtype = tagDetail[1].split('|')[1]
                if MAGtype != '부정부사':
                    tag = 'UNKNOWN'

        if tag == 'SY' and word not in exceptSymbal:
            tag = 'UNKNOWN'

        if tagType == 'Inflect':
            word = expression.split('/')[0]
            tag = firstTag

        dataSet.append(word)
        dataSet.append(tag)

        dataList.append(dataSet)

    index = 0
    while True:
        if index >= len(dataList):
            break

        data = dataList[index]

        if mode == 'Review':
            if data[1] == 'EC':
                if index - 1 >= 0 and index + 1 < len(dataList):
                    if dataList[index + 1][1][0] == 'V':
                        if dataList[index + 1][1] == 'VV':
                            index += 1
                            continue
                        if dataList[index - 1][0][len(dataList[index - 1][0]) - 1] == '다':
                            dataList[index - 1][0] = dataList[index - 1][0][:len(dataList[index - 1][0]) - 1]
                        dataList[index - 1][0] = dataList[index - 1][0] + data[0] + ' ' + dataList[index + 1][0]
                        dataList.pop(index + 1)
                        dataList.pop(index)
                        if dataList[index - 1][1][0] == 'V':
                            dataList[index - 1][0] = dataList[index - 1][0] + '다'
                        continue

            if data[1] == 'MM':
                if index + 1 < len(dataList):
                    if dataList[index + 1][1][0] == 'N':
                        data[0] = data[0] + dataList[index + 1][0]
                        data[1] = dataList[index + 1][1]
                        dataList.pop(index + 1)
                        index += 1
                        continue

        if data[1] == 'SN' or data[1] == 'NR':
            if index + 1 < len(dataList):
                targetIndex = index + 1
                if dataList[targetIndex][1] == 'NNBC':
                    data[0] = data[0] + dataList[targetIndex][0]
                    data[1] = 'NR'
                    dataList.pop(targetIndex)

                    if data[1] == 'NR':
                        if index - 1 >= 0:
                            targetIndex = index - 1
                            if dataList[targetIndex][1] == 'NR':
                                dataList[targetIndex][0] = dataList[targetIndex][0] + data[0]
                                dataList.pop(index)
                                continue
                    index += 1
                    continue

        if connectTag.__contains__(data[1]) == True:
            if data[0] == 'vs' or data[0] == 'VS' or data[0] == 'Vs':
                data[1] = 'UNKNOWN'
                if index + 1 < len(dataList):
                    if dataList[index + 1][0] == '.':
                        dataList[index + 1][1] = 'UNKNOWN'
                        index += 2
                continue                    

            if index - 1 >= 0:
                targetIndex = index - 1
                if data[1] == 'SY':
                    if index - 1 >= 0:
                        if dataList[index - 1][1] == 'SF' or dataList[index - 1][1] == 'SY':
                            dataList.pop(index)
                            continue

                    if index + 1 < len(dataList):
                        if dataList[index + 1][1] == 'SY':
                            index += 1
                            continue
                if connectTag.__contains__(dataList[targetIndex][1]):
                    if data[1] == 'SY':
                        if rawData.__contains__(dataList[targetIndex][0] + data[0]) == False:
                            data[1] = 'UNKNOWN'
                            index += 1
                            continue
                    if (data[1] != 'NNG' and dataList[targetIndex][1] == 'NNG') or (data[1] == 'NNG' and dataList[targetIndex][1] != data[1]):
                        index += 1
                        continue

                    if data[1] == 'NNG' and dataList[targetIndex][1] == data[1]:
                        dataList[targetIndex][1] = 'NNG'
                        dataList[targetIndex][0] = dataList[targetIndex][0] + ' '
                    else:
                        dataList[targetIndex][1] = 'NNP'
                        if rawData.__contains__(dataList[targetIndex][0] + data[0]) == False:
                            dataList[targetIndex][0] = dataList[targetIndex][0] + ' '

                    dataList[targetIndex][0] = dataList[targetIndex][0] + data[0]
                    dataList.pop(index)
                    continue

        if data[1][0] == 'V':
            data[0] = data[0] + '다'
            index += 1
            continue

        if data[1] == 'MAG':
            if index + 1 < len(dataList):
                if dataList[index + 1][1][0] == 'S':
                    index += 1
                    continue
                data[0] = data[0] + dataList[index + 1][0]
                data[1] = dataList[index + 1][1]
                if data[1][0] == 'V':
                    data[0] = data[0] + '다'
                dataList.pop(index + 1)
                index += 1
                continue

        if data[1] == 'XPN':
            if index + 1 < len(dataList):
                targetIndex = index + 1
                if dataList[targetIndex][1] == 'NNG':
                    dataList[targetIndex][0] = data[0] + dataList[targetIndex][0]
                    dataList.pop(index)
                    index += 1
                    continue

        index += 1

    for data in dataList:
        if targetTag == None:
            if exceptTag.__contains__(data[1]) == False:
                resultString.append(data[0])
        else:
            if data[1] in targetTag:
                resultString.append(data[0])

    return resultString

if __name__ == '__main__':
    data =  "안면인식장애" 
    print(DoNLP(data, mode='Review'))