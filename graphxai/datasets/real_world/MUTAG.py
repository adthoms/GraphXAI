import torch

from sklearn.model_selection import train_test_split

from torch_geometric.datasets import TUDataset

from graphxai.datasets.dataset import GraphDataset
from graphxai.utils import Explanation
from graphxai.datasets.utils.substruct_chem_match import match_NH2, match_substruct, MUTAG_NO2


class MUTAG(GraphDataset):
    '''
    GraphXAI implementation MUTAG dataset
        - Contains MUTAG with ground-truth 

    Args:
        root (str): Root directory in which to store the dataset
            locally.
        generate (bool, optional): (:default: :obj:`False`) 
    '''

    def __init__(self,
        root: str,
        use_fixed_split: bool = True, 
        generate: bool = True,
        split_sizes = (0.7, 0.2, 0.1),
        seed = None
        ):

        self.graphs = TUDataset(root=root, name='MUTAG')
        # self.graphs retains all qualitative and quantitative attributes from PyG

        self.__make_explanations()

        super().__init__(name = 'MUTAG', seed = seed, split_sizes = split_sizes)


    def __make_explanations(self):
        '''
        Makes explanations for MUTAG dataset
        '''

        self.explanations = []

        # Need to do substructure matching
        for i in range(len(self.graphs)):

            molG = self.get_graph_as_networkx(i)

            node_imp = torch.zeros(molG.number_of_nodes())

            nh2_matches = []

            # Screen for NH2:
            for n in molG.nodes():
                # Screen all nodes through match_NH2
                # match_NH2 is very quick
                m = match_NH2(molG, n)
                if m:
                    nh2_matches.append(m)

            # Screen for NO2:
            no2_matches = match_substruct(molG, MUTAG_NO2)
            
            for m in no2_matches:
                node_imp[m] = 1 # Mask-in those values

            for m in nh2_matches:
                node_imp[m] = 1

            # TODO: mask-in edge importance

            exp = Explanation(
                node_imp = node_imp
            )

            exp.set_whole_graph(self.graphs[i])

            self.explanations.append(exp)
