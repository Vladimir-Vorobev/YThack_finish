import pymorphy2
morph = pymorphy2.MorphAnalyzer()
mat_list = []

with open('mat.txt', 'r', encoding='cp1250') as f: # достаем список матных слов (я его на всякий случай убрал, там просто слово mmmaaattt)
    for line in f:
        for word in line.strip().split(', '):
            mat_list.append(word)

class antimat():

    def replace_mat(self, text): # возвращаем текст с зацензуренным матом. Пока не используется
        right_text = ''
        token = ''
        for l in text:
            if l.isalpha():
                token += l
            else:
                right_text += self.check_token(token) + l
                token = ''
        right_text += self.check_token(token)
        return right_text

    def find_mat(self, text): # проверяем, есть ли в тексте мат. Используется в регистрации
        token = ''
        for l in text:
            if l.isalpha():
                token += l
            else:
                if self.check_token(token) != token:
                    return True
                token = ''
        return False

    def check_token(self, token): # проверяем отдельный токен на мат
        if len(token) < 3:
            return token
        token_lower = token.lower()
        word = morph.parse(token_lower)[0].normal_form
        for mat in mat_list:
            if mat == word or mat == token_lower or (mat in word and (len(mat) / len(word) >= 0.65 or len(mat) >=5)):
                return  '*' * len(token)
        return token

am = antimat()