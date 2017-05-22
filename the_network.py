from concept_widget import *
from question_widget import *


class TheNetwork:
    parent_game = None

    def __init__(self, parent_game=None):
        self.concepts = []
        self.background = ''
        self.questions = None
        self.edges = None
        self.parent_game = parent_game

    def load(self, network_dict=None, questions=None, edges=None):
        self.questions = questions

        if network_dict is not None:            # print(network_dict)
            self.background = network_dict['background']
            self.concepts = network_dict['concepts']
            self.edges = edges
            for edge in self.edges:
                e = edge.split(',')
                if e[1] not in self.concepts[e[0]]:
                    self.concepts[e[0]][e[1]] = []
                self.concepts[e[0]][e[1]].append(e[2])

            for c_name, c in self.concepts.items():
                c['visible'] = c['level'] == 1
                c['widget'] = ConceptWidget(self)
                c['widget'].name = c_name

                pos = c['pos'].split(',')
                size = c['size'].split(',')
                c['widget'].image_id.source = c['image']
                c['widget'].image_id.pos = (int(pos[0]), int(pos[1]))
                c['widget'].image_id.size = (int(size[0]), int(size[1]))
                c['widget'].button_id.name = c_name + '_button'
                c['widget'].button_id.pos = (int(pos[0]), int(pos[1]))
                c['widget'].button_id.size = (int(size[0]), int(size[1]))

                c['q_widget'] = QuestionWidget(c_name, self)
                c['q_widget'].pos = (int(pos[0]), int(pos[1]))
                c['q_widget'].size = (int(size[0]), int(size[1]))
                for q_name, q_widget in c['q_widget'].q.items():
                    q_size = self.questions['general']['size'].split(',')
                    q_widget['image'].source = self.questions[q_name]['image']
                    q_widget['image'].pos = (int(pos[0]) + self.questions['general']['pos'],
                                             int(pos[1]) + self.questions[q_name]['pos'])
                    q_widget['image'].size = (int(q_size[0]), int(q_size[1]))
                    q_widget['button'].pos = (int(pos[0]) + self.questions['general']['pos'],
                                              int(pos[1]) + self.questions[q_name]['pos'])
                    q_widget['button'].size = (int(q_size[0]), int(q_size[1]))
                    q_widget['button'].name = c_name + '_' + q_name

                for q in c['q_widget'].q:
                    if q not in c:
                        c['q_widget'].q[q]['image'].disabled = True
                        c['q_widget'].q[q]['button'].disabled = True

    def question_pressed(self, concept, question):
        next_concepts = self.concepts[concept][question]
        for n in next_concepts:
            self.concepts[n]['visible'] = True

        self.parent_game.discovered_network.add((concept, question))
        self.parent_game.question_pressed(question)


    def concept_pressed(self, concept):
        self.parent_game.discovered_network.add((concept, 'questions'))
        self.parent_game.concept_pressed(concept)
