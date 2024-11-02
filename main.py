import sys

from PyQt5.QtGui import QTextLine
from PyQt5.QtWidgets import QWidget, QApplication, QStackedWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, \
    QComboBox, QButtonGroup, QHBoxLayout, QRadioButton
from coefficients import COEFFICIENTS, ATTRIBUTES, EARLY_DESIGN_MULTIPLIERS, EFFORT_MULTIPLIERS, SCALE_FACTORS

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()


        layout = QVBoxLayout()
        self.stacked_widgets = QStackedWidget()

        self.button_cocomo1 = QPushButton('COCOMO 1')
        self.button_cocomo2 = QPushButton('COCOMO 2')
        self.button_cocomo1.clicked.connect(lambda: self.stacked_widgets.setCurrentIndex(0))
        self.button_cocomo2.clicked.connect(lambda: self.stacked_widgets.setCurrentIndex(1))

        self.stacked_widgets.addWidget(self.cocomo_i_page())
        self.stacked_widgets.addWidget(self.cocomo_ii_page())

        layout.addWidget(self.button_cocomo1)
        layout.addWidget(self.button_cocomo2)
        layout.addWidget(self.stacked_widgets)

        self.setLayout(layout)
        self.show()


    def cocomo_i_page(self):

        page = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Кількість рядків (тисяч)"))
        self.text = QLineEdit()
        layout.addWidget(self.text)


        self.modes = QComboBox()
        self.modes.addItems(["Органічний", "Напіврозділений", "Вбудований"])
        layout.addWidget(self.modes)
        self.models = QComboBox()
        self.models.addItems(["Базова модель", "Проміжна модель"])
        self.models.currentIndexChanged.connect(self.loading_radio_buttons_cocomo_i)
        layout.addWidget(self.models)
        self.labelRes = QLabel()
        layout.addWidget(self.labelRes)

        calculateBtn = QPushButton("Розрахувати")
        layout.addWidget(calculateBtn)
        calculateBtn.clicked.connect(self.calculate_cocomo_i)

        self.intermediate_attr = QVBoxLayout()
        layout.addLayout(self.intermediate_attr)

        page.setLayout(layout)
        return page

    def calculate_basic_cocomo_i(self, size, a, b, c, d):
        PM = a * (size ** b)
        TM = c * (PM ** d)
        SS = PM / TM
        P = size / PM
        return PM, TM, SS, P

    def cocomo_i_intermediate(self, size, a, b, EAF):
        PM = EAF * a * (size ** b)
        return PM

    def calculate_cocomo_i(self):
        try:
            size = float(self.text.text())
            a, b, c , d = COEFFICIENTS[self.modes.currentText()]

            if self.models.currentText() == "Базова модель":
                PM, TM, SS, P = self.calculate_basic_cocomo_i(size, a, b, c, d)
                self.labelRes.setText(f"PM: {PM:.2f}\n"
                                      f"TM: {TM:.2f}\n"
                                      f"SS: {SS:.2f}\n"
                                      f"P: {P:.2f}")
            else:
                EAF = 1.0
                for i, group in enumerate(self.buttons_group):
                    selected_button = group.checkedButton()
                    if selected_button:
                        EAF *= float(selected_button.text())

                PM = self.cocomo_i_intermediate(size, a, b, EAF)
                TM = c * (PM ** d)
                SS = PM / TM
                P = size / PM

                self.labelRes.setText(f'EAF: {EAF:.2f}\n'
                                          f'Tрудовитрати (PM): {PM:.2f}\n'
                                          f'Час розробки (TM): {TM:.2f}\n'
                                          f'Середня чисельність (SS): {SS:.2f}\n'
                                          f'Продуктивність (P): {P:.2f}')
        except Exception as e:
            self.labelRes.setText(f"Помилка {e}")

    def loading_radio_buttons_cocomo_i(self):

        self.buttons_group = []

        for attr, values in ATTRIBUTES.items():
            attr_layout = QHBoxLayout()
            attr_label = QLabel(attr)
            attr_layout.addWidget(attr_label)
            button_group = QButtonGroup(self)
            self.buttons_group.append(button_group)

            for value in values:
                if value is not None:
                    radio_button = QRadioButton(str(value))
                    button_group.addButton(radio_button)
                    attr_layout.addWidget(radio_button)

            self.intermediate_attr.addLayout(attr_layout)

    def cocomo_ii_page(self):

        page = QWidget()
        main_layout = QVBoxLayout()

        main_layout.addWidget(QLabel("Кількість рядків (тисяч):"))
        self.lineText = QLineEdit()
        main_layout.addWidget(self.lineText)
        self.models_2 = QComboBox()
        self.models_2.addItems(["Early Design", "Post Architecture"])
        main_layout.addWidget(self.models_2)
        self.models_2.currentIndexChanged.connect(self.loading_cocomo_ii_buttons)

        self.main_buttons_layout = QVBoxLayout()


        main_layout.addLayout(self.main_buttons_layout)
        self.scale_layout = QVBoxLayout()

        self.scale_layout.addWidget(QLabel("Scale Factors"))

        main_layout.addLayout(self.scale_layout)



        self.loading_scale_factors_buttons_ii()
        self.loading_cocomo_ii_buttons()
        calculate_btn = QPushButton("Розрахувати")
        main_layout.addWidget(calculate_btn)
        calculate_btn.clicked.connect(self.calculate_cocomo_ii)

        stacked_widgets = QStackedWidget()

        self.labelRes2 = QLabel()
        main_layout.addWidget(self.labelRes2)


        page.setLayout(main_layout)
        return page

    def loading_cocomo_ii_buttons(self):
        # Очистка попередніх кнопок та вкладених лейаутів
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                if item.widget() is not None:
                    item.widget().deleteLater()
                elif item.layout() is not None:
                    clear_layout(item.layout())

        clear_layout(self.main_buttons_layout)

        if self.models_2.currentText() == "Early Design":
            self.buttons_group2 = []
            for attr, values in EARLY_DESIGN_MULTIPLIERS.items():
                attr_layout = QHBoxLayout()
                attr_layout.addWidget(QLabel(attr))
                button_group = QButtonGroup(self)
                self.buttons_group2.append(button_group)

                for value in values:
                    if value is not None:
                        radio_button = QRadioButton(str(value))
                        button_group.addButton(radio_button)
                        attr_layout.addWidget(radio_button)
                self.main_buttons_layout.addLayout(attr_layout)
        else:
            self.buttons_group3 = []
            for attr, values in EFFORT_MULTIPLIERS.items():
                attr_layout = QHBoxLayout()
                attr_layout.addWidget(QLabel(attr))
                button_group = QButtonGroup(self)
                self.buttons_group3.append(button_group)

                for value in values:
                    if value is not None:
                        radio_button = QRadioButton(str(value))
                        button_group.addButton(radio_button)
                        attr_layout.addWidget(radio_button)
                self.main_buttons_layout.addLayout(attr_layout)

    def loading_scale_factors_buttons_ii(self):
        self.buttons_group4 = []
        for attr, values in SCALE_FACTORS.items():
            attr_layout = QHBoxLayout()
            attr_layout.addWidget(QLabel(attr))
            button_group = QButtonGroup(self)
            self.buttons_group4.append(button_group)

            for value in values:
                if value is not None:
                    radio_button = QRadioButton(str(value))
                    button_group.addButton(radio_button)
                    attr_layout.addWidget(radio_button)
            self.scale_layout.addLayout(attr_layout)

    def calculate_cocomo_ii(self):
        try:
            # Отримання розміру проекту в KSLOC
            size = float(self.lineText.text())

            if self.models_2.currentText() == "Early Design":
                # Константи для "Early Design"
                A = 2.94
                B = 0.91
                C = 3.67
                D = 0.28

                # Обчислення EAF (Effort Adjustment Factor) для "Early Design"
                EAF = 1.0
                for group in self.buttons_group2:
                    selected_button = group.checkedButton()
                    if selected_button:
                        EAF *= float(selected_button.text())

                # Розрахунок суми значень SF для експоненти E
                SF_sum = sum(
                    float(group.checkedButton().text()) for group in self.buttons_group4 if group.checkedButton()
                )

                # Розрахунок експоненти E
                E = B + 0.01 * SF_sum

                # Розрахунок трудомісткості (PM)
                PM = EAF * A * (size ** E)

                # Розрахунок часу (TM) з множником SCED
                SCED = 1.0  # Стандартне значення SCED
                selected_sced_button = self.buttons_group2[-1].checkedButton()  # Остання група - SCED
                if selected_sced_button:
                    SCED = float(selected_sced_button.text())

                TM = C * (PM ** (D + 0.2 * (SCED - 1)))

                # Відображення результатів
                self.labelRes2.setText(f'EAF: {EAF:.2f}\n'
                                       f'PM: {PM:.2f} людино-місяців\n'
                                       f'TM: {TM:.2f} місяців')

            elif self.models_2.currentText() == "Post Architecture":
                # Константи для "Post Architecture"
                A = 2.45
                B = 0.91
                C = 3.67
                D = 0.28

                # Обчислення EAF для "Post Architecture"
                EAF = 1.0
                for group in self.buttons_group3:
                    selected_button = group.checkedButton()
                    if selected_button:
                        EAF *= float(selected_button.text())

                # Розрахунок суми значень SF для експоненти E
                SF_sum = sum(
                    float(group.checkedButton().text()) for group in self.buttons_group4 if group.checkedButton()
                )

                # Розрахунок експоненти E
                E = B + 0.01 * SF_sum

                # Розрахунок трудомісткості (PM) без SCED
                PM_NS = EAF * A * (size ** E)

                # Розрахунок часу (TM) з урахуванням SCED
                SCED = 1.0  # Стандартне значення SCED
                selected_sced_button = self.buttons_group3[-1].checkedButton()  # Остання група - SCED
                if selected_sced_button:
                    SCED = float(selected_sced_button.text())

                TM = SCED * C * (PM_NS ** (D + 0.2 * (E - B)))

                # Відображення результатів
                self.labelRes2.setText(f'EAF: {EAF:.2f}\n'
                                       f'PM: {PM_NS:.2f} людино-місяців\n'
                                       f'TM: {TM:.2f} місяців')

        except Exception as e:
            self.labelRes2.setText(f"Помилка {e}")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    wind = MainWindow()
    wind.show()
    app.exec_()