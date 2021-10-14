from rocrate.rocrate import ROCrate
from rocrate.utils import as_list, is_url
from collections import deque


class ROCratePlus(ROCrate):
    """
    Extending ROCrate with more things!
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: add this defaults to a file like ro-crate-js
        back_back_links = []
        self.defaults = dict(back_links={}, back_back_links=set(back_back_links))
        self._subgraph_by_id = {}
        self._subgraph = []

    def resolve(self, items, pathArray, subgraph=False):
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
        cd = deque(pathArray)
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
                    value = self.referenceToItem(val)
                    if '@id' in val and any(value):
                        id = val["@id"]
                        if id not in resolvedIds:
                            potentialItem = self.referenceToItem(val)
                            if 'includes' in p:
                                for key in p['includes']:
                                    if p['includes'][key] in as_list(potentialItem[key]):
                                        resolvedArray.append(potentialItem)
                                        resolvedIds[id] = 1
                            elif 'matchFn' in p:
                                if not p['matchFn'](potentialItem) is None:
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
            if item['@id'] not in self._subgraph_by_id:
                self._subgraph_by_id[item['@id']] = 1
                self._subgraph.append(item)

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

    def backLinkItem(self, item):

        for key in list(item):
            if key != "@id" and key != "@reverse":
                for part in as_list(item[key]):
                    target = self.referenceToItem(part)
                    if key not in self.defaults['back_links']:
                        back_link = None
                    else:
                        back_link = self.defaults['back_links'][key]
                    # Dealing with one of the known structural properties
                    if target and back_link:
                        if not target[back_link]:
                            target[back_link] = [{"@id": item["@id"]}]
                        else:
                            as_list(target[back_link]).append({"@id": item["@id"]})

                    elif not back_link and target is not None and not key in self.defaults['back_back_links']:
                        # We are linking to something
                        # print(f"Doing a back link", key + ': ' + target['@id'] + ':' + item['@id'])
                        if '@reverse' not in target:
                            target["@reverse"] = {}
                        if key not in target["@reverse"]:
                            target["@reverse"][key] = []

                        got_this_reverse_already = False
                        for r in target["@reverse"][key]:
                            if r["@id"] == item["@id"]:
                                got_this_reverse_already = True

                        if not got_this_reverse_already:
                            # console.log("Back linking", key)
                            target["@reverse"][key].append({"@id": item["@id"]})
                            # print(target)

    def addBackLinks(self):
        json = self.root_dataset.as_jsonld()
        self.backLinkItem(json)
        for item in self.default_entities:
            json = item.as_jsonld()
            self.backLinkItem(json)
        for item in self.contextual_entities:
            json = item.as_jsonld()
            self.backLinkItem(json)
        for item in self.data_entities:
            json = item.as_jsonld()
            self.backLinkItem(json)

    # See if a value (could be a string or an object) is a reference to something
    def referenceToItem(self, value):
        # Check if node is a reference to something else
        # If it is, return the something else
        if type(value).__name__ == 'dict':
            if '@id' in value:
                _id = value["@id"]
                if is_url(_id):
                    _id = _id
                elif _id.startswith('#'):
                    _id = _id
                else:
                    _id = '#' + _id
                deref = super().dereference(_id)
                if deref is not None:
                    return deref.as_jsonld()
                else:
                    return None
            else:
                return None
        else:
            return None
