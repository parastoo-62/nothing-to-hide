'''
Classes to perform crawling of pages.
'''
import networkx
import tqdm
import tweepy

GRAPH_FILE = 'test.yaml'  # TODO: remove hardecoded file


class Crawler():
    '''
    Parent crawler class.
    '''
    pass


class RecursiveCrawler(Crawler):
    '''
    Recursively crawl the followers lists to generate a larger list of
    known nodes.
    '''
    def __init__(self, api):
        '''
        :param api: Tweepy API object.
        '''
        self.leaves = []
        self.api = api

        self.read_graph_file()
        self.update_leaves()

    def fetch_followers(self, handle):
        '''
        Find the users who follow a given account.
        '''
        for follower in tqdm.tqdm(tweepy.Cursor(self.api.followers, handle).items()):
            if follower.followers_count > 0:
                self.graph.add_node(follower.screen_name.lower())
                self.graph.add_edge(follower.screen_name.lower(), handle.lower())
        self.write_graph_file()

    def fetch_following(self, handle):
        self.graph.add_node(handle)
        for userid in tqdm.tqdm(tweepy.Cursor(self.api.friends_ids, handle).items()):
            user = self.api.get_user(userid)
            self.graph.add_node(user.screen_name.lower())
            self.graph.add_edge(handle, user.screen_name.lower())
        self.write_graph_file()

    def read_graph_file(self):
        '''
        Read a graph file.
        '''
        self.graph = networkx.read_yaml(GRAPH_FILE)
        if self.graph is None:
            self.graph = networkx.DiGraph()
            self.write_graph_file()

    def run_round(self):
        '''
        Run a round for all users that do not have known followers in
        the current graph state.
        '''
        for user in tqdm.tqdm(self.leaves):
            self.fetch_followers(user)

    def update_leaves(self):
        '''
        Find all leaf nodes (nodes with no incoming connections). The
        followers for these nodes have not been downloaded.
        '''
        self.leaves = [n for n in self.graph if self.graph.in_degree(n) == 0]

    def write_graph_file(self):
        '''
        Write the graph file to disk.
        '''
        networkx.write_yaml(self.graph, GRAPH_FILE)
