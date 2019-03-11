import sys
import time
from collections import Counter, defaultdict

import jieba_fast
import jieba_fast.analyse
import jieba_fast.posseg
from flask import stream_with_context, request, Response, Flask, logging, \
    jsonify, render_template

app = Flask('server')
logger = logging.create_logger(app)
# jieba_fast.enable_parallel(4)
# word_dict_paths=[r'./jieba_dict/jieba_dict.txt',
#            r'./jieba_dict/baidu_2word.txt',r'./jieba_dict/baidu_3word.txt',
#            r"./jieba_dict/baidu_4word.txt",r'./jieba_dict/baidu_5word.txt',
#            r'./jieba_dict/other_basic_word.txt']
# for path in word_dict_paths:
#     jieba_fast.load_userdict(path)


stopwords_paths = [r'./jieba_dict/stopwords停用词-中文.txt',
                   r"./jieba_dict/stopwords停用词-英文.txt",
                   r'./jieba_dict/stopwords停用词-特殊符号.txt']


def stopwordslist(filepath):
    stopwords = [line.strip() for line in
                 open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords


stopwords = []
for path in stopwords_paths:
    stopwords += stopwordslist(path)


def build_info_list(count_info):
    data = []
    for word, count in count_info:
        word_info = {}
        word_info["word"] = word
        word_info['count'] = count
        data.append(word_info)
    return data


def div_result(result):
    length = len(result)
    per = int(length / 10)
    str_list = []
    for n in range(10):
        str = result[per * n:per * (n + 1)]
        str_list.append(str)
    return str_list


def get_topK(text, topK):
    text = jieba_fast.cut(text)
    result_str = []
    for word in text:
        if word not in stopwords:
            if word != '\t':
                result_str.append(word)
    count = Counter(result_str)
    topk_words = count.most_common(topK)
    per_data = build_info_list(topk_words)
    return per_data


@app.route('/', methods=['GET'])
def get():
    return render_template('posts.html')


@app.route('/fenci', methods=['POST'])
def fenci():
    start_time = time.time()
    logger.info(start_time)
    file = request.files.get('file')
    topK = request.form.get("topK", '20')
    text = request.form.get('text')
    json_dict = {}
    if file:
        try:
            text_body = ''.join(file.read().decode().split()).replace('，',
                                                                      '').replace(
                '。', '').replace('？', "").replace('“', '').replace('”',
                                                                   '').replace(
                '！', '')
        except UnicodeDecodeError:
            return '请确认文件格式为utf-8'
    elif text:
        text_body = "".join(text.split()).replace('，', '').replace('。',
                                                                   '').replace(
            '？', "").replace('“', '').replace('”', '').replace('！', '')
    else:
        return '请传入文本'
    size = sys.getsizeof(text_body)
    if size > 20000:
        text_list = div_result(text_body)
        logger.info('大文件')
        def generate():
            json_dict = {'data': []}
            origin_data = []
            mydict = defaultdict(int)
            n = 0
            for text in text_list:
                n += 1
                per_data = get_topK(text, int(topK))
                origin_data.extend(per_data)
                for info in origin_data:
                    mydict[info['word']] += info['count']
                mylist = sorted(mydict.items(), key=lambda x: x[1],
                                reverse=True)
                data = []
                for k in mylist[:int(topK)]:
                    info = {}
                    info['word'] = k[0]
                    info['count'] = k[1]
                    data.append(info)
                json_dict["data"] = data
                json_dict['total_words'] = len(text_body)
                json_dict['key_words'] = sum(
                    [word_info['count'] for word_info in data])
                json_dict['keyrate'] = "%.2f" % ((json_dict['key_words'] / len(
                    text_body)) * 100) + '%' if len(text_body) else 0
                if n < 10:
                    yield str(data)
                else:
                    yield str(json_dict)
        return Response(stream_with_context(generate()))
    else:
        logger.info(time.time() - start_time)
        data = get_topK(text_body, int(topK))
        json_dict["data"] = data
        json_dict['total_words'] = len(text_body)
        json_dict['key_words'] = sum([word_info['count'] for word_info in data])
        json_dict['keyrate'] = "%.2f" % ((json_dict['key_words'] / len(
            text_body)) * 100) + '%' if len(text_body) else 0
        return jsonify(json_dict)


if __name__ == "__main__":
    app.run(host='localhost', port=8081)
