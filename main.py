import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QRadioButton, \
    QButtonGroup, QHBoxLayout

COEFFICIENTS = {
    "Органічний": (2.4, 1.05, 2.5, 0.38),
    "Напіврозділений": (3.0, 1.12, 2.5, 0.35),
    "Вбудований": (3.6, 1.20, 2.5, 0.32)
}

ATTRIBUTES = {
    "Необхідна надійність ПЗ (RELY)": [0.75, 0.88, 1.00, 1.15, 1.40, None],
    "Розмір БД додатка (DATA)": [None, 0.94, 1.00, 1.08, 1.16, None],
    "Складність продукту (CPLX)": [0.70, 0.85, 1.00, 1.15, 1.30, 1.65],

    "Обмеження швидкодії при виконанні програми (TIME)": [None, None, 1.00, 1.11, 1.30, 1.66],
    "Обмеження пам'яті (STOR)": [None, None, 1.00, 1.06, 1.21, 1.56],
    "Нестійкість оточення віртуальної машини (VIRT)": [None, 0.87, 1.00, 1.15, 1.30, None],
    "Необхідний час відновлення (TURN)": [None, 0.87, 1.00, 1.07, 1.15, None],

    "Аналітичні здібності (ACAP)": [1.46, 1.19, 1.00, 0.86, 0.71, None],
    "Досвід розробки (AEXP)": [1.29, 1.13, 1.00, 0.91, 0.82, None],
    "Здібності до розробки ПЗ (PCAP)": [1.42, 1.17, 1.00, 0.86, 0.70, None],
    "Досвід використання віртуальних машин (VEXP)": [1.21, 1.10, 1.00, 0.90, None, None],
    "Досвід розробки на мовах програмування (LEXP)": [1.14, 1.07, 1.00, 0.95, None, None],

    "Застосування методів розробки ПЗ (MODP)": [1.24, 1.10, 1.00, 0.91, 0.82, None],
    "Використання інструментарію розробки ПЗ (TOOL)": [1.24, 1.10, 1.00, 0.91, 0.83, None],
    "Вимоги дотримання графіка розробки (SCED)": [1.23, 1.08, 1.00, 1.04, 1.10, None]
}

def cocomo_basic(size, a, b, c, d):
    PM = a * (size ** b)
    TM = c * (PM ** d)
    SS = PM / TM
    P = size / PM
    return PM, TM, SS, P

def cocomo_intermediate(size, a, b, EAF):
    PM = EAF * a * (size ** b)
    return PM

class COCOMOApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label_size = QLabel('KLOC:')
        self.input_size = QLineEdit(self)

        self.label_project_type = QLabel('Тип проєкту:')
        self.combo_project_type = QComboBox(self)
        self.combo_project_type.addItems(COEFFICIENTS.keys())

        self.label_level = QLabel('Рівень моделі:')
        self.combo_level = QComboBox(self)
        self.combo_level.addItems(['Базовий', 'Проміжний'])
        self.combo_level.currentTextChanged.connect(self.toggle_intermediate)

        self.button_calculate = QPushButton('Розрахувати')
        self.button_calculate.clicked.connect(self.calculate)

        self.result_label = QLabel('Результати з\'являться тут')

        layout.addWidget(self.label_size)
        layout.addWidget(self.input_size)
        layout.addWidget(self.label_project_type)
        layout.addWidget(self.combo_project_type)
        layout.addWidget(self.label_level)
        layout.addWidget(self.combo_level)

        self.intermediate_attributes_layout = QVBoxLayout()
        self.button_groups = []

        for attr_name, values in ATTRIBUTES.items():
            attr_layout = QHBoxLayout()
            attr_label = QLabel(attr_name)
            attr_layout.addWidget(attr_label)
            button_group = QButtonGroup(self)
            self.button_groups.append(button_group)

            for value in values:
                if value is not None:
                    radio_button = QRadioButton(str(value))
                    button_group.addButton(radio_button)
                    attr_layout.addWidget(radio_button)

            self.intermediate_attributes_layout.addLayout(attr_layout)

        layout.addLayout(self.intermediate_attributes_layout)
        layout.addWidget(self.button_calculate)
        layout.addWidget(self.result_label)

        self.setLayout(layout)
        self.toggle_intermediate('Базовий')
        self.setWindowTitle('COCOMO Model')
        self.show()

    def toggle_intermediate(self, level):
        for i in range(self.intermediate_attributes_layout.count()):
            item = self.intermediate_attributes_layout.itemAt(i)
            if isinstance(item, QHBoxLayout):

                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if widget:
                        widget.setVisible(level == 'Проміжний')

    def calculate(self):
        try:
            project_type = self.combo_project_type.currentText()
            level = self.combo_level.currentText()

            a, b, c, d = COEFFICIENTS[project_type]
            size = float(self.input_size.text())

            if level == 'Базовий':
                PM, TM, SS, P = cocomo_basic(size, a, b, c, d)
                self.result_label.setText(f'Тип проєкту: {project_type}\n'
                                          f'Tрудовитрати (PM): {PM:.2f}\n'
                                          f'Час розробки (TM): {TM:.2f}\n'
                                          f'Середня чисельність (SS): {SS:.2f}\n'
                                          f'Продуктивність (P): {P:.2f}')
            else:
                EAF = 1.0
                for i, group in enumerate(self.button_groups):
                    selected_button = group.checkedButton()
                    if selected_button:
                        EAF *= float(selected_button.text())

                PM = cocomo_intermediate(size, a, b, EAF)
                TM = EAF * (c * (PM ** d))
                SS = EAF * PM / TM
                P = EAF * size / PM

                self.result_label.setText(f'Тип проєкту: {project_type}\n'
                                          f'EAF: {EAF:.2f}\n'
                                          f'Tрудовитрати (PM): {PM:.2f}\n'
                                          f'Час розробки (TM): {TM:.2f}\n'
                                          f'Середня чисельність (SS): {SS:.2f}\n'
                                          f'Продуктивність (P): {P:.2f}')

        except Exception as e:
            self.result_label.setText(f'Виникла помилка: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = COCOMOApp()
    sys.exit(app.exec_())
