import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parents[1]
MEDIA=bool(importlib.util.find_spec('PIL') and importlib.util.find_spec('reportlab'))


@unittest.skipUnless(MEDIA,'Optional creative production dependencies absent')
class CreativeLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('proof_renderer',ROOT/'scripts/render_proof.py')
        cls.renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.renderer)

    def card(self,layout):
        return dict(headline='Make the next step clear.',body='One audience. One message. One approved theme.',
                    cta='Start with one brief',caption='Original fictional sample.',layout=layout)

    def test_long_token_wrap_stays_within_measured_width(self):
        from PIL import ImageFont
        font=ImageFont.truetype(str(self.renderer.BOLD),91)
        original='W'*40
        lines=self.renderer.wrap(original,font,870)
        self.assertTrue(all(font.getlength(line)<=870 for line in lines))
        self.assertEqual(''.join(lines),original)

    def test_unknown_layout_fails_without_any_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                self.renderer.render_card(self.card('unknown'),1,Path(tmp),'#80ead2')
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_supported_layouts_are_visually_distinct_and_editable(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            pixels=[]
            for n,layout in enumerate(('statement','editorial','split'),1):
                self.renderer.render_card(self.card(layout),n,Path(tmp),'#80ead2')
                image=Image.open(Path(tmp)/f'card-{n:03}.png')
                self.assertEqual(image.size,(1080,1920));pixels.append(image.tobytes())
                svg=ElementTree.fromstring((Path(tmp)/f'card-{n:03}.svg').read_text())
                self.assertEqual(svg.attrib['viewBox'],'0 0 1080 1920')
                self.assertEqual(svg.attrib['data-layout'],layout)
                texts=' '.join(node.text or '' for node in svg.iter() if node.tag.endswith('text'))
                self.assertIn('Make the next step clear.',texts)
                self.assertIn('ORIGINAL SPEC CONCEPT',texts)
                self.assertNotIn('APPROVED CLIENT CONCEPT',texts)
            self.assertEqual(len(set(pixels)),3)

    def test_statement_is_default_for_existing_jobs(self):
        with tempfile.TemporaryDirectory() as tmp:
            card=self.card('statement');card.pop('layout')
            self.renderer.render_card(card,1,Path(tmp),'#80ead2')
            svg=ElementTree.fromstring((Path(tmp)/'card-001.svg').read_text())
            self.assertEqual(svg.attrib['data-layout'],'statement')

    def test_dark_accent_keeps_split_headline_and_cta_visible(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            card=dict(self.card('split'),headline='Visible headline')
            self.renderer.render_card(card,1,Path(tmp),'#101a23')
            image=Image.open(Path(tmp)/'card-001.png')
            for bounds in [(100,450,970,580),(130,1610,950,1660)]:
                self.assertGreater(len(image.crop(bounds).getcolors()),1)
            svg=ElementTree.fromstring((Path(tmp)/'card-001.svg').read_text())
            text_nodes=[node for node in svg.iter() if node.tag.endswith('text')]
            for value in ['Visible headline',card['cta']]:
                node=next(node for node in text_nodes if node.text==value)
                self.assertNotEqual(node.attrib['fill'],'#101a23')

    def test_text_is_escaped_and_commission_label_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            card=self.card('editorial');card['headline']='Clear <steps> & next actions'
            self.renderer.render_card(card,1,Path(tmp),'#80ead2',specimen=False)
            svg=ElementTree.fromstring((Path(tmp)/'card-001.svg').read_text())
            texts=' '.join(node.text or '' for node in svg.iter() if node.tag.endswith('text'))
            self.assertIn('<steps>',texts);self.assertIn('APPROVED CLIENT CONCEPT',texts)
            self.assertNotIn('script',[node.tag.split('}')[-1] for node in svg.iter()])

    def test_invalid_palette_or_excessive_copy_does_not_export_partial_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            for card,accent in [(self.card('statement'),'not-a-color'),
                                (dict(self.card('split'),headline='word '*100),'#80ead2')]:
                with self.assertRaises(ValueError):self.renderer.render_card(card,1,Path(tmp),accent)
                self.assertEqual(list(Path(tmp).iterdir()),[])

    @unittest.skipUnless(importlib.util.find_spec('pypdf'),'Optional PDF inspection dependency absent')
    def test_proof_pdf_embeds_the_same_fonts_used_for_card_copy(self):
        from pypdf import PdfReader
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            jobs=json.loads((ROOT/'config/examples/creative_layouts.json').read_text())
            job=jobs[0]
            images=[self.renderer.render_card(c,n,root,job['accent']) for n,c in enumerate(job['cards'],1)]
            self.renderer.pdf(job,images,root/'proof.pdf')
            reader=PdfReader(root/'proof.pdf')
            fonts=[f.get_object() for f in reader.pages[0]['/Resources']['/Font'].values()]
            embedded=[f for f in fonts if '/FontDescriptor' in f and '/FontFile2' in f['/FontDescriptor']]
            self.assertGreaterEqual(len(embedded),2)
            self.assertIn('Northstar Example Studio',reader.pages[0].extract_text())

    @unittest.skipUnless(importlib.util.find_spec('pypdf'),'Optional PDF inspection dependency absent')
    def test_wide_company_title_fits_proof_page(self):
        from pypdf import PdfReader
        from reportlab.pdfbase import pdfmetrics
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            job=json.loads((ROOT/'config/examples/creative_layouts.json').read_text())[0]
            job['company']='Worldwide Engineering Management Solutions'
            self.renderer.pdf(job,[],root/'proof.pdf')
            title_sizes=[]
            def visit(text,cm,tm,font,size):
                if job['company'] in text:title_sizes.append(size)
            PdfReader(root/'proof.pdf').pages[0].extract_text(visitor_text=visit)
            self.assertEqual(len(title_sizes),1)
            self.assertLessEqual(pdfmetrics.stringWidth(job['company'],'MoneyfallProofBold',title_sizes[0]),532.01)


if __name__=='__main__':unittest.main()
