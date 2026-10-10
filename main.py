import random
from collections import Counter

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView

COULEURS = {
    1: (1, 0, 0, 1),        # Rouge
    2: (0, 1, 0, 1),        # Vert
    3: (0, 0, 1, 1),        # Bleu
    4: (1, 1, 0, 1),        # Jaune
    5: (1, 0, 1, 1),        # Magenta
    6: (0, 1, 1, 1),        # Cyan
    7: (1, 0.65, 0, 1),     # Orange
    8: (0.5, 0, 0.5, 1),    # Violet
    9: (1, 1, 1, 1),        # Blanc
    10: (0, 0, 0, 1),       # Noir
    11: (0.5, 0.5, 0.5, 1), # Gris
    12: (0.65, 0.16, 0.16, 1), # Marron
    13: (1, 0.75, 0.8, 1),  # Rose
    14: (0.5, 0.5, 0, 1),   # Olive
    15: (0, 0.5, 0.5, 1),   # Teal
}

COULEUR_FOND_CARREAU = (0.8, 0.8, 0.8, 1)

def generer_combinaison_secrete(difficulte):
    if difficulte == 4:
        couleurs = list(COULEURS.keys())
        return random.choices(couleurs, k=4)
    else:
        couleurs = list(range(1, 10))
        if difficulte == 1:
            return random.sample(couleurs, 4)
        elif difficulte == 2:
            while True:
                comb = random.choices(couleurs, k=4)
                counts = sorted(Counter(comb).values())
                if counts in [[1, 1, 1, 1], [1, 1, 2]]:
                    return comb
        else:
            return random.choices(couleurs, k=4)


class PopupMessage(ModalView):
    def __init__(self, titre, message, **kwargs):
        super().__init__(size_hint=(0.85, 0.35), auto_dismiss=True, **kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text=f"[b]{titre}[/b]", markup=True, font_size='18sp'))
        layout.add_widget(Label(text=message, halign='center', font_size='14sp'))
        btn = Button(text="OK", size_hint=(1, 0.35))
        btn.bind(on_release=self.dismiss)
        layout.add_widget(btn)
        self.add_widget(layout)


class MastermindKivy(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=8, **kwargs)
        self.difficulte = 1
        self.essai_actuel = 1
        self.partie_terminee = False
        self.couleur_selectionnee = None
        self.propositions = {l: [None, None, None, None] for l in range(1, 11)}
        
        self.build_ui()
        Clock.schedule_once(lambda dt: self.demander_difficulte(), 0.5)

    def build_ui(self):
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5)
        header.add_widget(Label(text="[b]MasterMajid[/b]", markup=True, font_size='20sp'))
        
        self.secret_layout = BoxLayout(spacing=10, size_hint=(None, None), size=(180, 35), pos_hint={'center_x': 0.5})
        self.secret_buttons = []
        for i in range(4):
            btn = Button(background_normal='', background_color=COULEUR_FOND_CARREAU)
            self.secret_layout.add_widget(btn)
            self.secret_buttons.append(btn)
        header.add_widget(self.secret_layout)
        self.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1))
        self.plateau_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.plateau_grid.bind(minimum_height=self.plateau_grid.setter('height'))
        
        self.carreaux_boutons = {}
        self.labels_bp = {}
        self.labels_mp = {}

        for l in range(10, 0, -1):
            row = BoxLayout(spacing=5, size_hint_y=None, height=40)
            row.add_widget(Label(text=f"E{l}", size_hint_x=None, width=30))
            
            self.carreaux_boutons[l] = []
            for c in range(4):
                btn = Button(background_normal='', background_color=COULEUR_FOND_CARREAU)
                btn.bind(on_release=lambda instance, line=l, col=c: self.clic_carreau(line, col))
                row.add_widget(btn)
                self.carreaux_boutons[l].append(btn)
            
            lb_bp = Label(text="-", size_hint_x=None, width=35, color=(0, 1, 0, 1))
            lb_mp = Label(text="-", size_hint_x=None, width=35, color=(1, 0.5, 0, 1))
            self.labels_bp[l] = lb_bp
            self.labels_mp[l] = lb_mp
            row.add_widget(lb_bp)
            row.add_widget(lb_mp)
            
            self.plateau_grid.add_widget(row)
            
        scroll.add_widget(self.plateau_grid)
        self.add_widget(scroll)

        self.palette_grid = GridLayout(cols=5, spacing=5, size_hint_y=None, height=90)
        self.palette_buttons = {}
        for num, color in COULEURS.items():
            btn = Button(background_normal='', background_color=color)
            btn.bind(on_release=lambda instance, n=num: self.choisir_couleur(n))
            self.palette_buttons[num] = btn
            self.palette_grid.add_widget(btn)
        self.add_widget(self.palette_grid)

        actions = BoxLayout(spacing=10, size_hint_y=None, height=45)
        btn_valider = Button(text="Valider", background_color=(0.2, 0.7, 0.2, 1))
        btn_valider.bind(on_release=lambda x: self.valider_ligne())
        btn_voir = Button(text="Voir / Aband.", background_color=(0.8, 0.3, 0.2, 1))
        btn_voir.bind(on_release=lambda x: self.abandonner_et_voir())
        btn_relancer = Button(text="Nouveau", background_color=(0.2, 0.5, 0.8, 1))
        btn_relancer.bind(on_release=lambda x: self.demander_difficulte())
        
        actions.add_widget(btn_valider)
        actions.add_widget(btn_voir)
        actions.add_widget(btn_relancer)
        self.add_widget(actions)

    def demander_difficulte(self):
        view = ModalView(size_hint=(0.9, 0.5), auto_dismiss=False)
        box = BoxLayout(orientation='vertical', padding=15, spacing=10)
        box.add_widget(Label(text="[b]Choisir la difficulté[/b]", markup=True, font_size='18sp'))
        
        niveaux = [
            ("1 - Facile (Sans doublons)", 1),
            ("2 - Intermédiaire (Max 1 doublon)", 2),
            ("3 - Difficile (Libre)", 3),
            ("4 - Hyper difficile (15 couleurs)", 4),
        ]
        
        for txt, n in niveaux:
            btn = Button(text=txt, font_size='14sp')
            btn.bind(on_release=lambda instance, lvl=n: self.demarrer_partie(lvl, view))
            box.add_widget(btn)
            
        view.add_widget(box)
        view.open()

    def demarrer_partie(self, difficulte, modal_view):
        modal_view.dismiss()
        self.difficulte = difficulte
        self.essai_actuel = 1
        self.partie_terminee = False
        self.couleur_selectionnee = None
        self.combinaison_secrete = generer_combinaison_secrete(self.difficulte)
        
        for btn in self.secret_buttons:
            btn.background_color = COULEUR_FOND_CARREAU
            
        for num, btn in self.palette_buttons.items():
            btn.disabled = (num >= 10 and self.difficulte != 4)
            btn.opacity = 1.0 if not btn.disabled else 0.2

        for l in range(1, 11):
            self.propositions[l] = [None, None, None, None]
            self.labels_bp[l].text = "-"
            self.labels_mp[l].text = "-"
            for col in range(4):
                self.carreaux_boutons[l][col].background_color = COULEUR_FOND_CARREAU

    def choisir_couleur(self, numero_couleur):
        self.couleur_selectionnee = numero_couleur

    def clic_carreau(self, ligne, col):
        if self.partie_terminee or ligne != self.essai_actuel:
            return

        couleur_actuelle = self.propositions[ligne][col]
        if couleur_actuelle is not None:
            self.propositions[ligne][col] = None
            self.carreaux_boutons[ligne][col].background_color = COULEUR_FOND_CARREAU
            return

        if self.couleur_selectionnee is None:
            return

        simul = list(self.propositions[ligne])
        simul[col] = self.couleur_selectionnee
        posees = [c for c in simul if c is not None]

        if self.difficulte == 1 and len(posees) != len(set(posees)):
            PopupMessage("Attention", "Niveau Facile : Couleurs différentes uniquement !").open()
            return
        elif self.difficulte == 2:
            counts = Counter(posees).values()
            if any(q > 2 for q in counts) or list(counts).count(2) > 1:
                PopupMessage("Attention", "Niveau Intermédiaire : Max 1 seul doublon !").open()
                return

        self.propositions[ligne][col] = self.couleur_selectionnee
        self.carreaux_boutons[ligne][col].background_color = COULEURS[self.couleur_selectionnee]

    def valider_ligne(self):
        if self.partie_terminee:
            return

        prop = self.propositions.get(self.essai_actuel, [])
        if None in prop:
            PopupMessage("Incomplet", "Remplissez les 4 carreaux !").open()
            return

        counts = sorted(Counter(prop).values())
        if self.difficulte == 1 and len(set(prop)) < 4:
            PopupMessage("Invalide", "Facile : 4 couleurs différentes !").open()
            return
        elif self.difficulte == 2 and counts not in [[1, 1, 1, 1], [1, 1, 2]]:
            PopupMessage("Invalide", "Intermédiaire : Max 1 seul doublon !").open()
            return

        c_sec = list(self.combinaison_secrete)
        c_prop = list(prop)

        bp = 0
        for i in range(4):
            if c_prop[i] == c_sec[i]:
                bp += 1
                c_sec[i] = None
                c_prop[i] = None

        mp = 0
        for i in range(4):
            c = c_prop[i]
            if c is not None and c in c_sec:
                mp += 1
                c_sec[c_sec.index(c)] = None
                c_prop[i] = None

        self.labels_bp[self.essai_actuel].text = str(bp)
        self.labels_mp[self.essai_actuel].text = str(mp)

        if bp == 4:
            self.partie_terminee = True
            self.reveler_solution()
            PopupMessage("Bravo !", f"Gagné en {self.essai_actuel} coups !").open()
            return

        if self.essai_actuel >= 10:
            self.partie_terminee = True
            self.reveler_solution()
            PopupMessage("Perdu", "Partie terminée !").open()
            return

        self.essai_actuel += 1

    def abandonner_et_voir(self):
        if self.partie_terminee:
            return
        self.partie_terminee = True
        self.reveler_solution()
        PopupMessage("Abandon", "Vous avez abandonné. Solution affichée !").open()

    def reveler_solution(self):
        for i, num in enumerate(self.combinaison_secrete):
            self.secret_buttons[i].background_color = COULEURS[num]


class MasterMindApp(App):
    def build(self):
        self.title = "MasterMajid"
        return MastermindKivy()


if __name__ == "__main__":
    MasterMindApp().run()
