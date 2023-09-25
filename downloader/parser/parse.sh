#!/bin/bash

filename="20220610"
crawlDate="20220610"

#parse appstore
#server
scriptDir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
#input_dir=${scriptDir}/../../process/parse_result
input_file=${scriptDir}/../result/${crawlDate}/combination/${crawlDate}.json
resultDir=${scriptDir}/../process/parse_result/${crawlDate}
ch2en_path="/u/zl11/iosStorecrawl/data/ch2en.json"

#my mac
:'
scriptDir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
#input_dir=${scriptDir}/../result/
#input_file="/Users/andyli/Documents/Paper/ios_store_crawl/result/chinese_app.json"
input_file="/Users/andyli/Documents/Paper/ios_store_crawl/result/20211113.json"
resultDir=${scriptDir}/../result/20211113/
ch2en_path="/Users/andyli/Documents/Paper/ios_store_crawl/data/ch2en.json"
'

python3 parser.py --input_file $input_file --result_dir $resultDir --result_filename $filename --target "appstore" --ch2en_dictionary_file $ch2en_path
#python3 parser_ranking.py --input_file $input_file --result_dir $resultDir --result_filename $filename --target "appstore" --ch2en_dictionary_file $ch2en_path

#parse policy
#server
:'
scriptDir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
#input_dir=${scriptDir}/../../process/parse_result
input_file=${scriptDir}/../../result/policy/${crawlDate}/combination/${crawlDate}.json
resultDir=${scriptDir}/../../process/parse_result/policy/${crawlDate}
'

#my mac
:'
scriptDir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
#input_dir=${scriptDir}/../result/
#input_file=${scriptDir}/../result/20211112/1636788736.json
#input_file="/Users/andyli/Documents/Paper/ios_store_crawl/result/chinese_app.json"
input_file="/Users/andyli/Documents/Paper/ios_store_crawl/result/1637762149_policy.json"
resultDir=${scriptDir}/../result/
'

#python3 parser.py --input_file $input_file --result_dir $resultDir --result_filename $filename --target "policy"
