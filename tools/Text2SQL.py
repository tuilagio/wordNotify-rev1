# -*- coding: utf-8 -*-
from DB_Dictionary import DB_SqliteDictionary
from DB_Dictionary import TB_LanguageRecord
from DB_Dictionary import TB_LanguageCollection
from DB_Dictionary import TB_VocabularyRecord
from DB_Dictionary import TB_VocabularyCollection
from DB_Dictionary import TB_VocabularyDenotationRecord
from DB_Dictionary import TB_VocabularyDenotationCollection
from DB_Dictionary import QueryExecuter

db_Dict = DB_SqliteDictionary("DB_Dictionary_V1.db")
conn = db_Dict.createConnection()


def escapeSpecialCharracter(str):
    return str.replace("'", "\'").replace('"', '\"').replace('%', '\%').replace('&', '\&').replace('#', '\#')


def lineTextAnalyzis(line):
    """

    :rtype: object
    """
    values = line.split("\t")
    if len(values) == 4:
        vocabulary = values[0]
        meaning = values[1]
        type = values[2]
        tags = values[3]
        return vocabulary, meaning, type, tags  # (str, str, str, list of str/None)
    else:
        return None


def loadDataInDatabase(file_path, languageA, languageB):
    with open(file_path, 'r', encoding="utf-8", errors="surrogateescape") as fp:
        poolSize = 2
        vocabularyPool = []
        index = 0
        tb_LanguageColl = TB_LanguageCollection(conn)
        tb_VocabularyColl = TB_VocabularyCollection(conn)
        tb_VocabularyDenotationColl = TB_VocabularyDenotationCollection(conn)
        records = tb_LanguageColl.getDataByCondition(" Language= '{0}'".format(languageA))
        if len(records) >= 1:
            idLanguageA = records[0].id
        else:
            n_Record = TB_LanguageRecord(None, languageA)
            idLanguageA = tb_LanguageColl.insertRecord(n_Record)

        records = tb_LanguageColl.getDataByCondition(" Language= '{0}'".format(languageB))
        if len(records) >= 1:
            idLanguageB = records[0].id
        else:
            n_Record = TB_LanguageRecord(None, languageB)
            idLanguageB = tb_LanguageColl.insertRecord(n_Record)
        lineIndex = 0
        skipIndex = 0
        for line in fp:
            lineIndex = lineIndex + 1
            print(lineIndex)
            # skip the comment lines, which starts with #
            if line.startswith("#") or len(line) == 0:
                skipIndex = skipIndex + 1
                continue
            tupelValues = lineTextAnalyzis(line)
            if tupelValues is None:
                skipIndex = skipIndex + 1
                continue
            vocabulary = tupelValues[0]
            # get primary key of vocabulary in the database
            if index < poolSize:
                # Search in Database
                records = tb_VocabularyColl.getDataByCondition(
                    """ Vocabulary= "{0}" AND ID_Language={1} """.format(escapeSpecialCharracter(vocabulary),
                                                                         idLanguageA))
                if len(records) >= 1:
                    idVocabulary = records[0].id
                else:
                    n_Record = TB_VocabularyRecord(None, vocabulary, idLanguageA)
                    idVocabulary = tb_VocabularyColl.insertRecord(n_Record)
                    n_Record.id = idVocabulary
                    vocabularyPool.append(n_Record)
                    index = index + 1
            else:  # Search in vocabularyPool
                flag = False
                for record in vocabularyPool:
                    if vocabulary == record.vocabulary:
                        idVocabulary = record.id
                        flag = True
                        break
                if not flag:
                    n_Record = TB_VocabularyRecord(None, vocabulary, idLanguageA)
                    idVocabulary = tb_VocabularyColl.insertRecord(n_Record)
                    n_Record.id = idVocabulary
                    vocabularyPool.pop(0)
                    vocabularyPool.append(n_Record)
            # insert meaning into the database with id key of the vocabulary'''
            meaning = tupelValues[1]
            type = tupelValues[2]
            tags = tupelValues[3]
            n_Record = TB_VocabularyDenotationRecord(None, idVocabulary, type, idLanguageB, meaning, tags)
            idVocabularyDenotation = tb_VocabularyDenotationColl.insertRecord(n_Record)
        conn.commit()
        conn.close()
        print("skipped Lines from {0} :{1}/{2}".format(file_path, skipIndex, lineIndex))


# loadDataInDatabase("..\dicts\d-e.txt", "deutsch", "english")
print("Bitte überprüfen")
