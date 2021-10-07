import collections

from rocrate.rocrate import ROCrate
from rocrate.utils import *


class ROCratePlus(ROCrate):
    """
    Extending ROCrate with more things!
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # def __init__(self, crate_path):
    #     super().__init__(crate_path)

    def resolve(self, items, pathArray, subgraph=None):
        """
        :param items:
            A JSON-LD item or array of [item]
            object  must have a "property to follow eg
            resolve(item, {"property": "miltaryService"});
            and optionally a condition "includes", eg
            "includes": {"@type", "Action"}}
            and optionally, a function "matchFn" which takes an item as argument and
            returns a boolean, eg:
            "matchFn": (item) => item['@id'].match(/anzsrc-for/)
        :param pathArray:
            pathArray is an array of objects that represents a 'path' through the graph
        :param subgraph:
            subgraph is a boolean - if present and true, all intervening items during
            the traversal will be stored and can be retrieved with the subgraph()
            method
        :return:
            null, or an array of items
        """
        cd = collections.deque(pathArray)
        p = cd.popleft()
        pathArray = cd
        resolvedArray = []
        resolvedIds = {}
        items = as_list(items)
        for item in items:
            if '@reverse' in p and '@reverse' in item:
                item = item["@reverse"]
            if p['property'] in item:
                for val in as_list(item[p['property']]):
                    value = super().dereference(val["@id"])
                    if '@id' in val and any(value.as_jsonld()):
                        id = val["@id"]
                        if id not in resolvedIds:
                            potentialItem = super().dereference(val["@id"])
                            potentialItem = potentialItem.as_jsonld()
                        if 'includes' in p:
                            for includes in p.includes:
                                inc = includes.keys()
                                if as_list(potentialItem[inc]).includes(p.includes[inc]):
                                    resolvedArray.append(potentialItem)
                                    resolvedIds[id] = 1
                        elif 'matchFn' in p:
                            if potentialItem in p['matchFn']:
                                resolvedArray.append(potentialItem)
                                resolvedIds[id] = 1
                        else:
                            resolvedArray.append(potentialItem)
                            resolvedIds[id] = 1

        if len(resolvedArray) == 0:
            return None
        elif len(pathArray) > 0:
            if subgraph:
                self._store_in_subgraph(resolvedArray)
            return self.resolve(resolvedArray, pathArray, subgraph)
        else:
            if subgraph:
                self._store_in_subgraph(resolvedArray)
            return resolvedArray  # Found our final list of results

    def _store_in_subgraph(self, resolvedArray):
        for item in resolvedArray:
            if not self._subgraph_by_id[item['@id']]:
                self._subgraph_by_id[item['@id']] = 1
                self._subgraph.push(item)

    def resolveAll(self, items, pathArray):
        """
        resolveAll does a resolve but collects and deduplicates intermediate
        items. Its first returned value is the final items (ie what resolve(..))
        would have returned.
        """
        self._subgraph_by_id = {}
        self._subgraph = []
        finals = self.resolve(items, pathArray, True)
        return [finals, self._subgraph]
