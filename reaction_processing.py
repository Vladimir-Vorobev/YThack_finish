import numpy as np
import time
from modules import timer

# список всех веществ
substances = [
    'H2','Li','Na','K','Cu','Rb','Ag','Cs','Au','Fr','Ca','Zn','Sr','Cd','Ba','Hg','Ra','Cn','Cl2','O2','S','C','N','P','Al',
    'HCl','H2SO3','H2SO4','H2CO3',
    'Cu(OH)2','LiOH','NaOH',
    'CuO', 'SO3','SO2','CO2','LiO2','Na2O',
    'NaI', 'K2SO4', 'K2CO3', 'Ba(NO3)2',
]

# список всех реакций
reactions = [
    # 0 lvl
    [['Li'], ['water'], 'LiOH', '2Li + 2H2O -> 2LiOH + H2', 'Мне нужен гидроксид лития. Я его буду использовать для моего нового щелочного аккумулятора', 'Гидроксид лития можно получить в окислительно-восстановительной реакции. Для этого нужна вода', ['Li', 'OH']],
    [['SO3'], ['water'], 'H2SO4', 'SO3 + H2O -> H2SO4', 'Мне нужна серная кислота. Я буду ее использовать в минеральных удобрениях для моего сада', 'Серную кислоту можно получить, смешав оксид с водой', ['SO4']],
    [['CaCO3'], ['gorelka'], 'CaO', 'CaCO3 -> CaO + CO2', 'Мне нужен оксид кальция. Я его буду использовать для нейтрализации избыточной кислоты', 'Оксид кальция можно получить в реакции разложения при увеличении температуры', ['O', 'Ca']],
    [['SO2'], ['water'], 'H2SO3', 'SO2 + H2O -> H2SO3', 'Мне нужна сернистая кислота. С помощью нее я смогу законсервировать овощи из моего сада и отбелить шелковую рубашку', 'Сернистую кислоту можно получить, смешав оксид с водой', ['SO3']],
    [['H2', 'Cl2'], [''], 'HCl', 'H2 + Cl2 -> 2HCl', 'Мне нужна соляная кислота. Она мне поможет при дезинфекции помещения', 'Соляную кислоту можно получить в окислительно-восстановительной реакции. Необходимо два простых вещества', ['H', 'Cl']],
    [['CaO'], ['water'], 'Ca(OH)2', 'CaO + H2O -> Ca(OH)2', 'Мне нужен гидроксид кальция. Я хочу с помощью него побелить забор и деревья', 'Гидроксид кальция можно получить в реакции соединения с водой', ['Ca', 'O']],
    [['NaOH', 'HCl'], [''], 'NaCl', 'NaOH + HCl -> NaCl + Н2О', 'Мне нужна поваренная соль, дома у меня она закончилась, а в магазине пусто', 'Поваренная соль - хлорид натрия, ее можно получить в реакции обмена', ['Na', 'Cl']],
    [['NaBr', 'H2'], [''], 'NaBr', '2HBr + 2Na -> 2NaBr + H2', 'Мне нужен бромид натрия для устранения бессонницы и раздражительности', 'Бромид натрия можно получить в окислительно-восстановительной реакции с кислотой', ['Na', 'Br']],
    # [[], ['gorelka'], '', '', 'Мне нужен ', '', []],
    # [[], ['gorelka'], '', '', 'Мне нужен ', '', []],
    # [[], [''], '', '', 'Мне нужен ', '', []],
    # [[], [''], '', '', 'Мне нужен ', '', []],
    # [[], [''], '', '', 'Мне нужен ', '', []],
    # [[], [''], '', '', 'Мне нужен ', '', []],
    # [[], [''], '', '', 'Мне нужен ', '', []],

    # 1 lvl
    [['NaI', 'H2SO4'], [''], 'I2', 'NaI + H2SO4 -> H2S + H2O + I2 + Na2SO4', 'Мне нужен йод для раствора, дезинфецирующего раны', 'Йод можно получить в окислительно-восстановительной реакции с использованием кислоты', ['I', 'SO3', 'SO4']],
    [['K2CO3', 'H2SO4'], [''], 'K2SO4', 'H2SO4 + K2CO3 -> K2SO4 + K2SO4 + H2O + CO2', 'Мне нужен сульфат калия для удобрений', 'Сульфат калия можно получить в кислотно-щелочной реакции с использованием кислоты', ['K', 'SO4']],
    [['Ba(NO3)2', 'H2SO4'], [''], 'BaSO4', 'Ba(NO3)2 + H2SO4 -> BaSO4 + 2HNO3', 'Мне нужен сульфат бария для рентгенологических исследований пищевода', 'Сульфат бария можно получить в реакции обмена с использованием кислоты', ['Ba', 'SO4']],
    [['NaCl', 'AgNO3'], ['water'], 'NaNO3', 'NaCl + AgNO3 -> NaNO3 + AgCl', 'Мне нужна натриевая селитра для моих удобрений', 'Нитрат натрия можно получить в реакции обмена с поваренной солью в растворе', ['Ag', 'Cl', 'Na']],
    [['NaCl', 'AgNO3'], ['water'], 'AgCl', 'NaCl + AgNO3 -> NaNO3 + AgCl', 'Мне нужен хлорид серебра. Я его использую в моем эксперементальном радаре', 'Хлорид серебра можно получить в реакции обмена с поваренной солью в растворе', ['Ag', 'Cl', 'Na']],
    # [[], [''], '', '', 'Мне нужен йод для раствора, дезинфецирующего раны. Его можно получить в окислительно-восстановительной реакции', '', []],
    # [[], [''], '', '', 'Мне нужен йод для раствора, дезинфецирующего раны. Его можно получить в окислительно-восстановительной реакции', '', []],
    # [[], [''], '', '', 'Мне нужен йод для раствора, дезинфецирующего раны. Его можно получить в окислительно-восстановительной реакции', '', []],
    # [[], [''], '', '', 'Мне нужен йод для раствора, дезинфецирующего раны. Его можно получить в окислительно-восстановительной реакции', '', []],
    # [[], [''], '', '', 'Мне нужен йод для раствора, дезинфецирующего раны. Его можно получить в окислительно-восстановительной реакции', '', []],

    # 2 lvl
    [['NaI', 'MnO2', 'H2SO4'], [''], 'NaHSO4', '2NaI + MnO2 + 3H2SO4 -> 2NaHSO4 + MnSO4 + I2 + 2H2O', 'Мне нужен гидросульфат натрия для понижения pH в моем бассейне', 'Гидросульфат натрия можно получить в окислительно-восстановительной реакции с тремя реагентами', ['Na', 'H', 'SO4']],
    [['H2S', 'Cl2'], ['water'], 'H2SO4 и HCl', 'H2S + 4Cl2 + 4H2O -> H2SO4 + 8HCl', 'Мне нужны серная и соляная кислоты для моих минеральных удобрений и дезинфекции', 'Нужные кисслоты можно получить в окислительно-восстановительной реакции с газами и водой', ['H', 'S', 'Cl']],
    # [[], [''], '', '', 'Мне нужен йод для раствора, дезинфецирующего раны. Его можно получить в окислительно-восстановительной реакции', '', []],
    # [[], [''], '', '', 'Мне нужен йод для раствора, дезинфецирующего раны. Его можно получить в окислительно-восстановительной реакции', '', []],
    # [[], [''], '', '', 'Мне нужен йод для раствора, дезинфецирующего раны. Его можно получить в окислительно-восстановительной реакции', '', []],
]

# к каждой реакции добавляем укороченный список элементов, чтобы был возможен только однозначный ответ
for reaction in reactions:
    substances_special = []
    for i in range(len(substances)):
        metric = True
        for el in reaction[6]:
            if el in substances[i]:
                metric = False
        if metric:
            substances_special.append(substances[i])
    reaction.append(substances_special)

# количество реакций, из которого можно выбирать реакцию для игрока с определенным рангом
lvl_length = {
    0: 8,
    1: 13,
    2: 15,
}

# шаблоны для ответа на неправильные реакции
incorrect = {'reaction': 'incorrect', 'substance': 'Попробуйте еще раз, у Вас все получится)', 'money': 0}
incorrect_multiplayer = {'reaction': 'incorrect', 'substance': 'Попробуйте еще раз, у Вас все получится)', 'store': 0}

class reaction_processing():
    def play(self, data, type): # выбираем реакцию для пользователя
        reactions_copy = reactions.copy()
        index_main = np.random.randint(0, lvl_length[data['rang']])
        substances_copy = reactions_copy[index_main][7].copy()
        list = reactions_copy[index_main][0].copy() # берем те вещества, которые точно должны быть
        for i in range(10 - len(list)): # добираем до 10 веществ произвольными веществами
            index = np.random.randint(0, len(substances_copy))
            while substances_copy[index] in reactions_copy[index_main][0]:
                index = np.random.randint(0, len(substances_copy))
            list.append(substances_copy[index])
            del substances_copy[index]
        list_to_send = []
        np.random.shuffle(list) # перемешиваем массив
        while len(list) != 0: # и еще раз перемешиваем массив другим способом
            index = np.random.randint(0, len(list))
            list_to_send.append(list[index])
            del list[index]
        res = {'substances': list_to_send, 'question': reactions_copy[index_main][4], 'index': index_main}
        if type == 'play_alone': # если игра одиночная, добавляем подсказку
            res['hint'] = reactions_copy[index_main][5]
        return res

    def play_alone_answer(self, data): # проверяем ответ в одиночной игре
        data['list_of_substances'] = data['list_of_substances'][1:-1].split(', ')
        data['list_of_objects'] = data['list_of_objects'][1:-1].split(', ')
        if len(data['list_of_substances']) != len(reactions[data['index']][0]) or len(data['list_of_objects']) != len(reactions[data['index']][1]):
            return incorrect
        for i in data['list_of_substances']:
            if i not in reactions[data['index']][0]:
                return incorrect
        for i in data['list_of_objects']:
            if i not in reactions[data['index']][1]:
                return incorrect
        sum = np.random.randint(25, 31)
        return {'reaction': reactions[data['index']][2], 'substance': reactions[data['index']][3], 'money': sum}

    def multi_play_answer(self, data): # проверяем ответ в мультиплеере
        data['list_of_substances'] = data['list_of_substances'][1:-1].split(', ')
        data['list_of_objects'] = data['list_of_objects'][1:-1].split(', ')
        if 'water' in data['list_of_objects']: # если выбрана вода, замедляем реакцию в зависимости от уровня прокачки воды
            time.sleep(data['water_vlv'])
        if 'gorelka' in data['list_of_objects']: # если выбрана горелка, замедляем реакцию в зависимости от уровня прокачки горелки
            time.sleep(data['gorelka_vlv'])
        if len(data['list_of_substances']) != len(reactions[data['index']][0]) or len(data['list_of_objects']) != len(reactions[data['index']][1]):
            return incorrect_multiplayer
        for i in data['list_of_substances']:
            if i not in reactions[data['index']][0]:
                return incorrect_multiplayer
        for i in data['list_of_objects']:
            if i not in reactions[data['index']][1]:
                return incorrect_multiplayer
        store = np.random.randint(50, 61)
        return {'reaction': reactions[data['index']][2], 'substance': reactions[data['index']][3], 'store': store}

rep = reaction_processing()