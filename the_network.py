from concept_widget import *
from question_widget import *


class TheNetwork:
    parent_game = None

    def __init__(self, parent_game=None):
        self.concepts = None
        self.background = ''
        self.questions = None
        self.edges = None
        self.parent_game = parent_game
        self.size = None
        self.image_dir = ''

    def load(self, network_dict=None, questions=None, edges=None, app_size=None):
        self.questions = questions
        self.size = app_size

        if network_dict is not None:            # print(network_dict)
            self.image_dir = network_dict['dir']
            self.background = self.image_dir + network_dict['background']
            self.concepts = network_dict['concepts']
            self.edges = edges

            for edge in self.edges:
                e = edge.split(',')
                if e[1] not in self.concepts[e[0]]:
                    self.concepts[e[0]][e[1]] = []
                self.concepts[e[0]][e[1]].append(e[2])

            self.walk_the_graph(node="alien")

            for c_name, c in self.concepts.items():
                c['visible'] = c['level'] == 1
                c['new'] = None
                c['widget'] = ConceptWidget(self)
                c['widget'].name = c_name

                c['widget'].image_id.source = self.image_dir + c['image'][0]
                c['widget'].button_id.name = c_name + '_button'

                c['q_widget'] = QuestionWidget(c_name, self)
                for q_name, q_widget in c['q_widget'].q.items():
                    q_size = [float(x) for x in self.questions['general']['size'].split(',')]
                    q_widget['image'].source = 'items/' + self.questions[q_name]['image']
                    q_widget['button'].name = c_name + '_' + q_name

                for q in c['q_widget'].q:
                    if q not in c:
                        c['q_widget'].q[q]['image'].disabled = True
                        c['q_widget'].q[q]['button'].disabled = True
            self.update_pos_size(app_size)

    def update_pos_size(self, app_size):
        self.size = app_size
        if self.concepts:
            for c_name, c in self.concepts.items():
                pos = [float(x) for x in c['pos'].split(',')]
                size = [float(x) for x in c['size'].split(',')]
                c['widget'].image_id.pos = (int(pos[0] * self.size[0]), int(pos[1] * self.size[1]))
                c['widget'].image_id.size = (int(size[0] * self.size[0]), int(size[1] * self.size[1]))
                c['widget'].button_id.pos = c['widget'].image_id.pos
                c['widget'].button_id.size = c['widget'].image_id.size

                c['q_widget'].pos = (int(pos[0] * self.size[0]), int(pos[1] * self.size[1]))
                c['q_widget'].size = (int(size[0] * self.size[0]), int(size[1] * self.size[1]))
                for q_name, q_widget in c['q_widget'].q.items():
                    q_size = [float(x) for x in self.questions['general']['size'].split(',')]
                    q_widget['image'].pos = (int((pos[0] + self.questions['general']['pos']) * self.size[0]),
                                             int((pos[1] + self.questions[q_name]['pos']) * self.size[1]))
                    q_widget['image'].size = (int(q_size[0] * self.size[0]), int(q_size[1] * self.size[1]))
                    q_widget['button'].pos = q_widget['image'].pos
                    q_widget['button'].size = q_widget['image'].size

    def question_pressed(self, concept, question):
        next_concepts = self.concepts[concept][question]
        for n in next_concepts:
            self.concepts[n]['visible'] = True
            self.concepts[n]['new'] = concept

        self.parent_game.discovered_network.add((concept, question))
        self.parent_game.question_pressed(question)

    def concept_pressed(self, concept):
        self.parent_game.discovered_network.add((concept, 'questions'))
        self.parent_game.concept_pressed(concept)

    def walk_the_graph(self, q_str="", edge=None, node=None):
        if edge:
            q_str += " " + edge + " "

        q_str += " " + self.concepts[node]["image"][0] + " "
        next_nodes = []
        for e in self.edges:
            link = e.split(',')
            if link[0] == node:
                next_nodes.append(link[2])
                self.walk_the_graph(q_str, link[1], link[2])
        if len(next_nodes) == 0:
            print(q_str)
