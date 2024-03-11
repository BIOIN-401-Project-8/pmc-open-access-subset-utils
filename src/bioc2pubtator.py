from bioc import BioCAnnotation, BioCDocument, BioCRelation
from bioc.pubtator import PubTator, PubTatorAnn, PubTatorRel


class CustomPubTatorAnn(PubTatorAnn):
    def __str__(self) -> str:
        return super().__str__().rstrip('\t')

def bioc2pubtator_ann(biocann: BioCAnnotation, pmid: str) -> PubTatorAnn:
    ann = CustomPubTatorAnn(
        pmid=pmid,
        start=biocann.locations[0].offset,
        end=biocann.locations[0].offset + biocann.locations[0].length,
        text=biocann.text,
        type=biocann.infons['type'],
        id=biocann.infons.get('identifier', biocann.text)
    )
    return ann

class CustomPubTatorRel(PubTatorRel):
    def __str__(self) -> str:
        row = [self.pmid, self.type, self.id1, self.id2]
        if self.neg is not None:
            row.append(self.neg)
        return '\t'.join(row)

def bioc2pubtator_rel(biocrel: BioCRelation, pmid: str) -> PubTatorRel:
    rel = CustomPubTatorRel(
        pmid=pmid,
        type=biocrel.infons['type'],
        id1=biocrel.infons['role1'].rsplit('|', 1)[-1],
        id2=biocrel.infons['role2'].rsplit('|', 1)[-1],
        neg=biocrel.infons.get('neg')
    )
    return rel


def bioc2pubtator(doc: BioCDocument) -> PubTator:
    pubdoc = PubTator()
    pmid = doc.id
    pubdoc.pmid = pmid
    pubdoc.title = " ".join([passage.text for passage in doc.passages if passage.infons['type'] == 'title'])
    pubdoc.abstract = " ".join([passage.text for passage in doc.passages if passage.infons['type'] == 'abstract'])
    for passage in doc.passages:
        for ann in passage.annotations:
            pubann = bioc2pubtator_ann(ann, pmid)
            pubdoc.annotations.append(pubann)
    for rel in doc.relations:
        pubrel = bioc2pubtator_rel(rel, pmid)
        pubdoc.relations.append(pubrel)
    return pubdoc
