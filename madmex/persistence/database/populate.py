'''
Created on Jun 2, 2016

@author: agutierrez
'''
from madmex.persistence.database.connection import Unit, Organization, \
    Legend, Algorithm, Satellite, Band, Description, ProductType, Host, Command, \
    Sensor, BASE, ENGINE
from sqlalchemy.orm.session import sessionmaker
from madmex.configuration import SETTINGS
#from sqlalchemy import create_engine

#ENGINE = create_engine(getattr(SETTINGS, 'ANTARES_DATABASE'))

def populate_database():
    '''
    This method populates the database with the information that won't change
    over time. It is possible to create a fresh copy of the database.
    '''
    klass = sessionmaker(bind=ENGINE, autoflush=False)
    session = klass()
    units_array = [
        {
            'name':'nanometer',
            'unit':'nm'
        },
        {
            'name':'micrometer',
            'unit':'\u03BCu'
        },
        {
            'name':'percent',
            'unit':'%'
        },
        {
            'name':'digital number',
            'unit':'dn'
        },
        {
            'name':'degree celcius',
            'unit':'\u2103'
        },
    ]
    organizations_array = [
        {
            'name':'CONABIO',
            'description':'Comisi\u00F3n Nacional para el Conocimiento y Uso de la Biodiversidad.',
            'country':'M\u00E9xico',
            'url':'http://www.conabio.gob.mx/'
        },
        {
            'name':'CONAFOR',
            'description':'Comisi\u00F3n Nacional Forestal.',
            'country':'M\u00E9xico',
            'url':'http://www.conafor.gob.mx/web/'
        },
        {
            'name':'INEGI',
            'description':'Instituto Nacional de Estad\u00EDstica y Geograf\u00EDa.',
            'country':'M\u00E9xico',
            'url':'http://www.inegi.org.mx/'
        },
        {
            'name':'BlackBridge',
            'description':'Berlin based imagery company.',
            'country':'Germany',
            'url':'http://www.blackbridge.com/'
        },
        {
            'name':'NASA',
            'description':'National Aeronautics and Space Administration',
            'country':'United States',
            'url':''
        },
        {
            'name':'Spot Image',
            'description':'Public limited imagery company.',
            'country':'United States',
            'url':'http://www.geo-airbusds.com/en/143-spot-satellite-imagery'
        },
        {
            'name':'ISRO',
            'description':'Indian Space Research Organization',
            'country':'India',
            'url':'http://www.isro.gov.in/'
        },
        {
            'name':'Digital Globe',
            'description':'American commercial vendor of space imagery and geospatial content.',
            'country':'United States',
            'url':'https://www.digitalglobe.com/'
        },
        {
            'name':'USGS',
            'description':'United States Geological Survey.',
            'country':'United States',
            'url':'http://www.usgs.gov/'
        },
    ]
    sensors_array = [
        {
            'name':'RE',
            'reference_name':'rapideye',
            'description':'RapidEye'
        },
        {
            'name':'SPOT-5',
            'reference_name':None,
            'description':'SPOT 5 HRG Multispectral.'
        },
        {
            'name':'SPOT-5-P',
            'reference_name':None,
            'description':'SPOT 5 HRG Panchromatic.'
        },
        {
            'name':'SPOT-6',
            'reference_name':None,
            'description':'SPOT-6'
        },
        {
            'name':'TM',
            'reference_name':None,
            'description':'Thematic Mapper.'
        },
        {
            'name':'ETM+',
            'reference_name':None,
            'description':'Enhanced Thematic Mapper Plus.'
        },
        {
            'name':'MODIS',
            'reference_name':None,
            'description':'Moderate-resolution Imaging Spectroradiometer'
        },
        {
            'name':'AWF',
            'reference_name':None,
            'description':'AWF'
        },
        {
            'name':'L-3',
            'reference_name':None,
            'description':'L-3'
        },
        {
            'name':'WV02',
            'reference_name':None,
            'description':'WorldView-2'
        },
        {
            'name':'OLI_TIRS',
            'reference_name':'oli_tirs',
            'description':'OLI TIRS'
        },
        {
            'name':'IRS-P6',
            'reference_name':None,
            'description':'Indian Remote-Sensing Satellite P6'
        },
    ]
    legends_array = [
        {
            'name':'madmex_legend_landsat_lcc_4.0',
            'styled_layer_descriptor':('<?xml version="1.0" ?><sld:StyledLayerDe'
                'scriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xm'
                'lns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.ope'
                'ngis.net/ogc" xmlns:sld="http://www.opengis.net/sld"><sld:User'
                'Layer><sld:LayerFeatureConstraints><sld:FeatureTypeConstraint/'
                '></sld:LayerFeatureConstraints><sld:UserStyle><sld:Name>madmex'
                '_lcc_landsat_1993_v4</sld:Name><sld:Title/><sld:FeatureTypeSty'
                'le><sld:Name/><sld:Rule><sld:RasterSymbolizer><sld:Geometry><o'
                'gc:PropertyName>grid</ogc:PropertyName></sld:Geometry><sld:Opa'
                'city>1</sld:Opacity><sld:ColorMap type="intervals"><sld:ColorM'
                'apEntry color="#FFFFFF" label=" " opacity="1.0" quantity="0"/>'
                '<sld:ColorMapEntry color="#005500" label="Bosque De Coniferas"'
                ' opacity="1.0" quantity="1"/><sld:ColorMapEntry color="#006C00'
                '" label="Bosque De Coniferas Herbacea" opacity="1.0" quantity='
                '"2"/><sld:ColorMapEntry color="#00CF98" label="Bosque De Encin'
                'o-Pino Y Pino-Encino Herbacea" opacity="1.0" quantity="3"/><sl'
                'd:ColorMapEntry color="#FFFF7F" label="Agricultura" opacity="1'
                '.0" quantity="4"/><sld:ColorMapEntry color="#E59900" label="Ma'
                'torral Xerofilo Herbacea" opacity="1.0" quantity="5"/><sld:Col'
                'orMapEntry color="#AA55FF" label="Selvas Secas Arborea" opacit'
                'y="1.0" quantity="6"/><sld:ColorMapEntry color="#008B00" label'
                '="Bosque De Coniferas Arborea" opacity="1.0" quantity="7"/><sl'
                'd:ColorMapEntry color="#C7C8BC" label="Suelo Desnudo" opacity='
                '"1.0" quantity="8"/><sld:ColorMapEntry color="#AAFFFF" label="'
                'Vegetacion Hidrofila" opacity="1.0" quantity="9"/><sld:ColorMa'
                'pEntry color="#AA007F" label="Selvas Secas" opacity="1.0" quan'
                'tity="10"/><sld:ColorMapEntry color="#00AA00" label="Bosque De'
                ' Encino " opacity="1.0" quantity="11"/><sld:ColorMapEntry colo'
                'r="#AA00FF" label="Selvas Secas Herbacea" opacity="1.0" quanti'
                'ty="12"/><sld:ColorMapEntry color="#00C100" label="Bosque De E'
                'ncino Arborea" opacity="1.0" quantity="13"/><sld:ColorMapEntry'
                ' color="#AAAA7F" label="Pastizales" opacity="1.0" quantity="14'
                '"/><sld:ColorMapEntry color="#FF00FF" label="Selvas Humedas Y '
                'Subhumedas Y Bosque Mesofilo Arborea" opacity="1.0" quantity="'
                '15"/><sld:ColorMapEntry color="#9F6A00" label="Matorral Xerofi'
                'lo" opacity="1.0" quantity="16"/><sld:ColorMapEntry color="#00'
                'D800" label="Bosque De Encino Herbacea" opacity="1.0" quantity'
                '="17"/><sld:ColorMapEntry color="#000000" label="Urbano Y Cons'
                'truido" opacity="1.0" quantity="18"/><sld:ColorMapEntry color='
                '"#0000FF" label="Cuerpo De Agua" opacity="1.0" quantity="19"/>'
                '<sld:ColorMapEntry color="#BD7E00" label="Matorral Xerofilo Ar'
                'borea" opacity="1.0" quantity="20"/><sld:ColorMapEntry color="'
                '#00FFFF" label="Vegetacion Hidrofila Herbacea" opacity="1.0" q'
                'uantity="21"/><sld:ColorMapEntry color="#00AA7F" label="Bosque'
                ' De Encino-Pino Y Pino-Encino" opacity="1.0" quantity="22"/><s'
                'ld:ColorMapEntry color="#FF007F" label="Selvas Humedas Y Subhu'
                'medas Y Bosque Mesofilo" opacity="1.0" quantity="23"/><sld:Col'
                'orMapEntry color="#00C893" label="Bosque De Encino-Pino Y Pino'
                '-Encino Arborea" opacity="1.0" quantity="24"/><sld:ColorMapEnt'
                'ry color="#B000B0" label="Selvas Humedas Y Subhumedas Y Bosque'
                ' Mesofilo Herbacea" opacity="1.0" quantity="25"/><sld:ColorMap'
                'Entry color="#AAAA7F" label="Pastizales Herbacea" opacity="1.0'
                '" quantity="26"/></sld:ColorMap></sld:RasterSymbolizer></sld:R'
                'ule></sld:FeatureTypeStyle></sld:UserStyle></sld:UserLayer></s'
                'ld:StyledLayerDescriptor>')
        },
        {
            'name':'madmex_legend_landsat_lcc_4.1',
            'styled_layer_descriptor':('<?xml version="1.0" ?><sld:StyledLayerDe'
            'scriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:'
            'gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net'
            '/ogc" xmlns:sld="http://www.opengis.net/sld"><sld:UserLayer><sld:L'
            'ayerFeatureConstraints><sld:FeatureTypeConstraint/></sld:LayerFeat'
            'ureConstraints><sld:UserStyle><sld:Name>madmex_lcc_landsat_1993_v4'
            '</sld:Name><sld:Title/><sld:FeatureTypeStyle><sld:Name/><sld:Rule>'
            '<sld:RasterSymbolizer><sld:Geometry><ogc:PropertyName>grid</ogc:Pr'
            'opertyName></sld:Geometry><sld:Opacity>1</sld:Opacity><sld:ColorMa'
            'p type="intervals"><sld:ColorMapEntry color="#75A8D4" label=" " op'
            'acity="1.0" quantity="0"/><sld:ColorMapEntry color="#006D00" label'
            '="Bosque de Ayarin; Cedro" opacity="1.0" quantity="1"/><sld:ColorM'
            'apEntry color="#00AA00" label="Bosque Encino(-Pino); Matorral Subt'
            'ropical" opacity="1.0" quantity="2"/><sld:ColorMapEntry color="#00'
            '5500" label="Bosque de Pino (-Encino); Abies; Oyamel; Tascate; Mat'
            'orral de Coniferas" opacity="1.0" quantity="3"/><sld:ColorMapEntry'
            ' color="#AAAA00" label="Matorral Submontano; Mequital Tropical; Bo'
            'sque Mezquital" opacity="1.0" quantity="4"/><sld:ColorMapEntry col'
            'or="#AA8000" label="Bosque de Mezquite; Matorral Desertico Microfi'
            'lo; Mezquital Desertico; Vegetacion de Galeria" opacity="1.0" quan'
            'tity="5"/><sld:ColorMapEntry color="#8BAA00" label="Chaparral" opa'
            'city="1.0" quantity="6"/><sld:ColorMapEntry color="#FF8000" label='
            '"Matorral Crasicaule" opacity="1.0" quantity="7"/><sld:ColorMapEnt'
            'ry color="#FF0000" label="Bosque Mesofilo de Montana; Selva Baja P'
            'erennifolio" opacity="1.0" quantity="8"/><sld:ColorMapEntry color='
            '"#AA007F" label="Selva Baja (Sub)Caducifolia; Espinosa (Caducifoli'
            'a); Palmar Inducido" opacity="1.0" quantity="9"/><sld:ColorMapEntr'
            'y color="#AA00FF" label="Selva Baja y Mediana (Espinosa) Subperenn'
            'ifolia; Selva de Galeria; Palmar Natural" opacity="1.0" quantity="'
            '10"/><sld:ColorMapEntry color="#FF007F" label="Selva Alta Subperen'
            'nifolia" opacity="1.0" quantity="11"/><sld:ColorMapEntry color="#F'
            'F00FF" label="Selva Alta y Mediana Perennifolia" opacity="1.0" qua'
            'ntity="12"/><sld:ColorMapEntry color="#FF55FF" label="Selva Median'
            'a (Sub) Caducifolia" opacity="1.0" quantity="13"/><sld:ColorMapEnt'
            'ry color="#AAFFFF" label="Tular" opacity="1.0" quantity="14"/><sld'
            ':ColorMapEntry color="#00FFFF" label="Popal" opacity="1.0" quantit'
            'y="15"/><sld:ColorMapEntry color="#FFAAFF" label="Manglar; Vegetac'
            'ion de Peten" opacity="1.0" quantity="16"/><sld:ColorMapEntry colo'
            'r="#E29700" label="Matorral Sarco-Crasicaule" opacity="1.0" quanti'
            'ty="17"/><sld:ColorMapEntry color="#BD7E00" label="Matorral Sarco-'
            'Crasicaule de Neblina" opacity="1.0" quantity="18"/><sld:ColorMapE'
            'ntry color="#966400" label="Matorral Sarcocaule" opacity="1.0" qua'
            'ntity="19"/><sld:ColorMapEntry color="#75ECAF" label="Vegetacion d'
            'e Dunas Costeras" opacity="1.0" quantity="20"/><sld:ColorMapEntry '
            'color="#C46200" label="Matorral Desertico Rosetofilo" opacity="1.0'
            '" quantity="21"/><sld:ColorMapEntry color="#AA5500" label="Matorra'
            'l Espinosa Tamaulipeco" opacity="1.0" quantity="22"/><sld:ColorMap'
            'Entry color="#6D3600" label="Matorral Rosetofilo Costero" opacity='
            '"1.0" quantity="23"/><sld:ColorMapEntry color="#00AA7F" label="Veg'
            'etacion de Desiertos Arenos" opacity="1.0" quantity="24"/><sld:Col'
            'orMapEntry color="#008A65" label="Vegetacion Halofila Hidrofila" o'
            'pacity="1.0" quantity="25"/><sld:ColorMapEntry color="#005941" lab'
            'el="Vegetacion Gipsofila Halofila Xerofila" opacity="1.0" quantity'
            '="26"/><sld:ColorMapEntry color="#AAAA7F" label="Pastizal y Sabana'
            '" opacity="1.0" quantity="27"/><sld:ColorMapEntry color="#FFFF7F" '
            'label="Agricultura" opacity="1.0" quantity="28"/><sld:ColorMapEntr'
            'y color="#0000FF" label="Agua" opacity="1.0" quantity="29"/><sld:C'
            'olorMapEntry color="#C7C8BC" label="Sin y Desprovisto de Vegetacio'
            'n" opacity="1.0" quantity="30"/><sld:ColorMapEntry color="#000000"'
            ' label="Urbana" opacity="1.0" quantity="31"/><sld:ColorMapEntry co'
            'lor="#55AB00" label="Bosque Inducido; Cultivado; de Galeria" opaci'
            'ty="1.0" quantity="123"/></sld:ColorMap></sld:RasterSymbolizer></s'
            'ld:Rule></sld:FeatureTypeStyle></sld:UserStyle></sld:UserLayer></s'
            'ld:StyledLayerDescriptor>')
        },
        {
            'name':'madmex_legend_malla_lcc_level3',
            'styled_layer_descriptor':'<?xml version="1.0" ?><sld:StyledLayerDe'
            'scriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:'
            'gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net'
            '/ogc" xmlns:sld="http://www.opengis.net/sld"><sld:UserLayer><sld:L'
            'ayerFeatureConstraints><sld:FeatureTypeConstraint/></sld:LayerFeat'
            'ureConstraints><sld:UserStyle><sld:Name>DF+Morelos</sld:Name><sld:'
            'Title/><sld:FeatureTypeStyle><sld:Name/><sld:Rule><sld:RasterSymbo'
            'lizer><sld:Geometry><ogc:PropertyName>grid</ogc:PropertyName></sld'
            ':Geometry><sld:Opacity>1</sld:Opacity><sld:ColorMap><sld:ColorMapE'
            'ntry color="#84c96f" label="Bosque de Ayarin" opacity="1.0" quanti'
            'ty="1"/><sld:ColorMapEntry color="#63f73e" label="Bosque de Cedro"'
            ' opacity="1.0" quantity="2"/><sld:ColorMapEntry color="#3cab32" la'
            'bel="Bosque de Oyamel" opacity="1.0" quantity="3"/><sld:ColorMapEn'
            'try color="#92a685" label="Bosque de Pino" opacity="1.0" quantity='
            '"4"/><sld:ColorMapEntry color="#cff7c6" label="Bosque de Tascate" '
            'opacity="1.0" quantity="5"/><sld:ColorMapEntry color="#88e04c" lab'
            'el="Bosque de Encino" opacity="1.0" quantity="6"/><sld:ColorMapEnt'
            'ry color="#7ca668" label="Bosque de Encino-Pino" opacity="1.0" qua'
            'ntity="7"/><sld:ColorMapEntry color="#91f27c" label="Bosque de Pin'
            'o-Encino" opacity="1.0" quantity="8"/><sld:ColorMapEntry color="#b'
            'bf09e" label="Bosque cultivado" opacity="1.0" quantity="9"/><sld:C'
            'olorMapEntry color="#46c72c" label="Bosque inducido" opacity="1.0"'
            ' quantity="10"/><sld:ColorMapEntry color="#ae3dd1" label="Bosque M'
            'esofilo de Montana" opacity="1.0" quantity="11"/><sld:ColorMapEntr'
            'y color="#dfb6e3" label="Selva Alta Perennifolia" opacity="1.0" qu'
            'antity="12"/><sld:ColorMapEntry color="#e880e6" label="Selva Baja '
            'Perennifolia" opacity="1.0" quantity="13"/><sld:ColorMapEntry colo'
            'r="#a772b5" label="Selva Mediana Perennifolia" opacity="1.0" quant'
            'ity="14"/><sld:ColorMapEntry color="#aa4fb8" label="Palmar natural'
            '" opacity="1.0" quantity="15"/><sld:ColorMapEntry color="#f23df2" '
            'label="Peten" opacity="1.0" quantity="16"/><sld:ColorMapEntry colo'
            'r="#f269f5" label="Selva da Galeria" opacity="1.0" quantity="17"/>'
            '<sld:ColorMapEntry color="#e6a1f0" label="Selva Alta Subperennifol'
            'ia" opacity="1.0" quantity="18"/><sld:ColorMapEntry color="#b58cb8'
            '" label="Selva Mediana Subperennifolia" opacity="1.0" quantity="19'
            '"/><sld:ColorMapEntry color="#c833f5" label="Selva Baja Espinosa S'
            'ubperennifolia" opacity="1.0" quantity="20"/><sld:ColorMapEntry co'
            'lor="#ac63ba" label="Bosque de Galeria" opacity="1.0" quantity="21'
            '"/><sld:ColorMapEntry color="#d94ff7" label="Palmar" opacity="1.0"'
            ' quantity="22"/><sld:ColorMapEntry color="#dc7afa" label="Palmar i'
            'nducido" opacity="1.0" quantity="23"/><sld:ColorMapEntry color="#b'
            '944c2" label="Vegetaci\u00F3n de Peten" opacity="1.0" quantity="24'
            '"/><sld:ColorMapEntry color="#d132ce" label="Manglar" opacity="1.0'
            '" quantity="25"/><sld:ColorMapEntry color="#cb5ced" label="Selva B'
            'aja Caducifolia" opacity="1.0" quantity="26"/><sld:ColorMapEntry c'
            'olor="#c68fcf" label="Selva Mediana Caducifolia" opacity="1.0" qua'
            'ntity="27"/><sld:ColorMapEntry color="#cd62d1" label="Selva Baja E'
            'spinosa Caducifolia" opacity="1.0" quantity="28"/><sld:ColorMapEnt'
            'ry color="#d98eed" label="Selva Baja Subcaducifolia" opacity="1.0"'
            ' quantity="29"/><sld:ColorMapEntry color="#c47acc" label="Selva Ba'
            'ja Espinosa" opacity="1.0" quantity="30"/><sld:ColorMapEntry color'
            '="#f250f0" label="Selva Mediana Subcaducifolia" opacity="1.0" quan'
            'tity="31"/><sld:ColorMapEntry color="#f0c990" label="Matorral Dese'
            'rtico Rosetofilo" opacity="1.0" quantity="43"/><sld:ColorMapEntry '
            'color="#d18a5a" label="Matorral Desertico RosetofiloVegetaci\u00F3'
            'n de Galeria" opacity="1.0" quantity="52"/><sld:ColorMapEntry colo'
            'r="#c2b8cc" label="Pastizal Halofilo" opacity="1.0" quantity="54"/'
            '><sld:ColorMapEntry color="#4b494d" label="Pastizal Natural" opaci'
            'ty="1.0" quantity="55"/><sld:ColorMapEntry color="#837e87" label="'
            'Pradera de Alta montana" opacity="1.0" quantity="56"/><sld:ColorMa'
            'pEntry color="#ebe4f2" label="Pastizal inducido" opacity="1.0" qua'
            'ntity="59"/><sld:ColorMapEntry color="#615c66" label="Pastizal Cul'
            'tivado" opacity="1.0" quantity="62"/><sld:ColorMapEntry color="#2c'
            'd4c0" label="Vegetaci\u00F3n Halofila Hidrofila" opacity="1.0" qua'
            'ntity="65"/><sld:ColorMapEntry color="#ffff73" label="Agricultura '
            'de Humedad" opacity="1.0" quantity="66"/><sld:ColorMapEntry color='
            '"#a8a800" label="Agricultura de Riego" opacity="1.0" quantity="67"'
            '/><sld:ColorMapEntry color="#ffe173" label="Agricultura de Tempora'
            'l" opacity="1.0" quantity="68"/><sld:ColorMapEntry color="#8289d9"'
            ' label="Acuicola" opacity="1.0" quantity="69"/><sld:ColorMapEntry '
            'color="#3832ed" label="Agua" opacity="1.0" quantity="70"/><sld:Col'
            'orMapEntry color="#ff5500" label="Asentamientos Humanos" opacity="'
            '1.0" quantity="71"/><sld:ColorMapEntry color="#a80000" label="Zona'
            ' Urbana" opacity="1.0" quantity="72"/><sld:ColorMapEntry color="#c'
            'ccccc" label="Sin Vegetaci\u00F3n aparente" opacity="1.0" quantity'
            '="73"/><sld:ColorMapEntry color="#b2b2b2" label="Desprovisto de Ve'
            'getaci\u00F3n" opacity="1.0" quantity="74"/></sld:ColorMap></sld:R'
            'asterSymbolizer></sld:Rule></sld:FeatureTypeStyle></sld:UserStyle>'
            '</sld:UserLayer></sld:StyledLayerDescriptor>'
        },
        {
            'name':'madmex_legend_malla_lcc_level2',
            'styled_layer_descriptor':'<?xml version="1.0" ?><sld:StyledLayerDe'
            'scriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:'
            'gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net'
            '/ogc" xmlns:sld="http://www.opengis.net/sld"><sld:UserLayer><sld:L'
            'ayerFeatureConstraints><sld:FeatureTypeConstraint/></sld:LayerFeat'
            'ureConstraints><sld:UserStyle><sld:Name>DF+Morelos</sld:Name><sld:'
            'Title/><sld:FeatureTypeStyle><sld:Name/><sld:Rule><sld:RasterSymbo'
            'lizer><sld:Geometry><ogc:PropertyName>grid</ogc:PropertyName></sld'
            ':Geometry><sld:Opacity>1</sld:Opacity><sld:ColorMap><sld:ColorMapE'
            'ntry color="#203c00" label="Bosque de Coniferas" opacity="1.0" qua'
            'ntity="1"/><sld:ColorMapEntry color="#46d836" label="Bosque de Enc'
            'ino" opacity="1.0" quantity="2"/><sld:ColorMapEntry color="#55aa7f'
            '" label="Bosque Mezclado" opacity="1.0" quantity="3"/><sld:ColorMa'
            'pEntry color="#aa007f" label="Selvas Humedas y Subhumedas y Bosque'
            ' Mesofilo" opacity="1.0" quantity="4"/><sld:ColorMapEntry color="#'
            '7d26cf" label="Selvas Secas" opacity="1.0" quantity="5"/><sld:Colo'
            'rMapEntry color="#d2691e" label="Matorral Xerofilo Arbustivo" opac'
            'ity="1.0" quantity="7"/><sld:ColorMapEntry color="#a5a581" label="'
            'Pastizales" opacity="1.0" quantity="8"/><sld:ColorMapEntry color="'
            '#f6e87e" label="Agricultura" opacity="1.0" quantity="10"/><sld:Col'
            'orMapEntry color="#0000ff" label="Agua" opacity="1.0" quantity="11'
            '"/><sld:ColorMapEntry color="#5c0000" label="Urbano y Construido" '
            'opacity="1.0" quantity="12"/><sld:ColorMapEntry color="#e0e0e0" la'
            'bel="Suelo Desnudo" opacity="1.0" quantity="13"/></sld:ColorMap></'
            'sld:RasterSymbolizer></sld:Rule></sld:FeatureTypeStyle></sld:UserS'
            'tyle></sld:UserLayer></sld:StyledLayerDescriptor>'
        },
        {
            'name':'madmex_legend_malla_lcc_level1',
            'styled_layer_descriptor':'<?xml version="1.0" ?><sld:StyledLayerDe'
            'scriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:'
            'gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net'
            '/ogc" xmlns:sld="http://www.opengis.net/sld"><sld:UserLayer><sld:L'
            'ayerFeatureConstraints><sld:FeatureTypeConstraint/></sld:LayerFeat'
            'ureConstraints><sld:UserStyle><sld:Name>DF+Morelos</sld:Name><sld:'
            'Title/><sld:FeatureTypeStyle><sld:Name/><sld:Rule><sld:RasterSymbo'
            'lizer><sld:Geometry><ogc:PropertyName>grid</ogc:PropertyName></sld'
            ':Geometry><sld:Opacity>1</sld:Opacity><sld:ColorMap><sld:ColorMapE'
            'ntry color="#203c00" label="Tierras forestales" opacity="1.0" quan'
            'tity="1"/><sld:ColorMapEntry color="#91916d" label="Praderas" opac'
            'ity="1.0" quantity="2"/><sld:ColorMapEntry color="#f6e87e" label="'
            'Tierras de uso agricola" opacity="1.0" quantity="4"/><sld:ColorMap'
            'Entry color="#0000ff" label="Agua" opacity="1.0" quantity="5"/><sl'
            'd:ColorMapEntry color="#5c0000" label="Asentamientos" opacity="1.0'
            '" quantity="6"/><sld:ColorMapEntry color="#e0e0e0" label="Otros" o'
            'pacity="1.0" quantity="7"/></sld:ColorMap></sld:RasterSymbolizer><'
            '/sld:Rule></sld:FeatureTypeStyle></sld:UserStyle></sld:UserLayer><'
            '/sld:StyledLayerDescriptor>'
        },
        {
            'name':'madmex_legend_landsat_lcc_4.2',
            'styled_layer_descriptor':'<?xml version="1.0" ?><sld:StyledLayerDe'
            'scriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:'
            'gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net'
            '/ogc" xmlns:sld="http://www.opengis.net/sld"><sld:UserLayer><sld:L'
            'ayerFeatureConstraints><sld:FeatureTypeConstraint/></sld:LayerFeat'
            'ureConstraints><sld:UserStyle><sld:Name>madmex_lcc_landsat_2000_v4'
            '.2</sld:Name><sld:Title/><sld:FeatureTypeStyle><sld:Name/><sld:Rul'
            'e><sld:RasterSymbolizer><sld:Geometry><ogc:PropertyName>grid</ogc:'
            'PropertyName></sld:Geometry><sld:Opacity>1</sld:Opacity><sld:Color'
            'Map type="intervals"><sld:ColorMapEntry color="#75a8d4" label=" " '
            'opacity="1.0" quantity="0"/><sld:ColorMapEntry color="#005100" lab'
            'el="Bosque de Ayarin; Cedro" opacity="1.0" quantity="1"/><sld:Colo'
            'rMapEntry color="#007e00" label="Bosque Encino(-Pino); Matorral Su'
            'btropical" opacity="1.0" quantity="2"/><sld:ColorMapEntry color="#'
            '003c00" label="Bosque de Pino (-Encino); Abies; Oyamel; Tascate; M'
            'atorral de Coniferas" opacity="1.0" quantity="3"/><sld:ColorMapEnt'
            'ry color="#aaaa00" label="Matorral Submontano; Mequital Tropical; '
            'Bosque Mezquital" opacity="1.0" quantity="4"/><sld:ColorMapEntry c'
            'olor="#aa8000" label="Bosque de Mezquite; Matorral Desertico Micro'
            'filo; Mezquital Desertico; Vegetacion de Galeria" opacity="1.0" qu'
            'antity="5"/><sld:ColorMapEntry color="#8baa00" label="Chaparral" o'
            'pacity="1.0" quantity="6"/><sld:ColorMapEntry color="#ffb265" labe'
            'l="Matorral Crasicaule" opacity="1.0" quantity="7"/><sld:ColorMapE'
            'ntry color="#00d900" label="Bosque Mesofilo de Montana; Selva Baja'
            ' Perennifolio" opacity="1.0" quantity="8"/><sld:ColorMapEntry colo'
            'r="#aa007f" label="Selva Baja (Sub)Caducifolia; Espinosa (Caducifo'
            'lia); Palmar Inducido" opacity="1.0" quantity="9"/><sld:ColorMapEn'
            'try color="#ff55ff" label="Selva Baja y Mediana (Espinosa) Subpere'
            'nnifolia; Selva de Galeria; Palmar Natural" opacity="1.0" quantity'
            '="10"/><sld:ColorMapEntry color="#ff557f" label="Selva Alta Subper'
            'ennifolia" opacity="1.0" quantity="11"/><sld:ColorMapEntry color="'
            '#ff007f" label="Selva Alta y Mediana Perennifolia" opacity="1.0" q'
            'uantity="12"/><sld:ColorMapEntry color="#ff55ff" label="Selva Medi'
            'ana (Sub) Caducifolia" opacity="1.0" quantity="13"/><sld:ColorMapE'
            'ntry color="#aaffff" label="Tular" opacity="1.0" quantity="14"/><s'
            'ld:ColorMapEntry color="#00ffff" label="Popal" opacity="1.0" quant'
            'ity="15"/><sld:ColorMapEntry color="#55aaff" label="Manglar; Veget'
            'acion de Peten" opacity="1.0" quantity="16"/><sld:ColorMapEntry co'
            'lor="#e29700" label="Matorral Sarco-Crasicaule" opacity="1.0" quan'
            'tity="17"/><sld:ColorMapEntry color="#bd7e00" label="Matorral Sarc'
            'o-Crasicaule de Neblina" opacity="1.0" quantity="18"/><sld:ColorMa'
            'pEntry color="#966400" label="Matorral Sarcocaule" opacity="1.0" q'
            'uantity="19"/><sld:ColorMapEntry color="#a2ecb1" label="Vegetacion'
            ' de Dunas Costeras" opacity="1.0" quantity="20"/><sld:ColorMapEntr'
            'y color="#c46200" label="Matorral Desertico Rosetofilo" opacity="1'
            '.0" quantity="21"/><sld:ColorMapEntry color="#aa5500" label="Mator'
            'ral Espinosa Tamaulipeco" opacity="1.0" quantity="22"/><sld:ColorM'
            'apEntry color="#6d3600" label="Matorral Rosetofilo Costero" opacit'
            'y="1.0" quantity="23"/><sld:ColorMapEntry color="#00aa7f" label="V'
            'egetacion de Desiertos Arenos" opacity="1.0" quantity="24"/><sld:C'
            'olorMapEntry color="#008a65" label="Vegetacion Halofila Hidrofila"'
            ' opacity="1.0" quantity="25"/><sld:ColorMapEntry color="#005941" l'
            'abel="Vegetacion Gipsofila Halofila Xerofila" opacity="1.0" quanti'
            'ty="26"/><sld:ColorMapEntry color="#e9e9af" label="Pastizal y Saba'
            'na" opacity="1.0" quantity="27"/><sld:ColorMapEntry color="#faff98'
            '" label="Agricultura" opacity="1.0" quantity="28"/><sld:ColorMapEn'
            'try color="#00007f" label="Agua" opacity="1.0" quantity="29"/><sld'
            ':ColorMapEntry color="#c7c8bc" label="Sin y Desprovisto de Vegetac'
            'ion" opacity="1.0" quantity="30"/><sld:ColorMapEntry color="#4d100'
            '9" label="Urbana" opacity="1.0" quantity="31"/><sld:ColorMapEntry '
            'color="#6daa50" label="Bosque secondario" opacity="1.0" quantity="'
            '100"/><sld:ColorMapEntry color="#3a7500" label="Bosque Inducido; C'
            'ultivado; de Galeria" opacity="1.0" quantity="123"/><sld:ColorMapE'
            'ntry color="#0b5923" label="Bosque de Pino-Encino; Matorral de Con'
            'iferas" opacity="1.0" quantity="124"/><sld:ColorMapEntry color="#f'
            'faaff" label="Selva secundaria" opacity="1.0" quantity="200"/></sl'
            'd:ColorMap></sld:RasterSymbolizer></sld:Rule></sld:FeatureTypeStyl'
            'e></sld:UserStyle></sld:UserLayer></sld:StyledLayerDescriptor>'
        },
    ]
    descriptions_array = [
        {
            'description':'Landsat Raw Imagery',
            'creator':'NASA',
            'publisher':'USGS'
        },
        {
            'description':'Landsat LEDAPS Calibrated Products',
            'creator':'CONABIO',
            'publisher':'CONABIO'
        },
        {
            'description':'Landsat FMASK Derived Data Masks',
            'creator':'CONABIO',
            'publisher':'CONABIO'
        },
        {
            'description':'RapidEye Raw Imagery',
            'creator':'BlackBridge',
            'publisher':'BlackBridge'
        },
        {
            'description':'SPOT 5 Georeferenced by CONABIO',
            'creator':'CONABIO',
            'publisher':'CONABIO'
        },
    ]
    product_type_array = [
        {
            'level':1,
            'name':'Level 1B',
            'short_name':'L1B',
            'description':'RapidEye Raw Imagery'
        },
        {
            'level':2,
            'name':'Level 3A',
            'short_name':'L3A',
            'description':'RapidEye Raw Imagery'
        },
        {
            'level':3,
            'name':'LEDAPS TOA reflectance',
            'short_name':'lndcal',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':4,
            'name':'LEDAPS Surface reflectance',
            'short_name':'lndsr',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':5,
            'name':'LEDAPS Temperature',
            'short_name':'lndth',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':6,
            'name':'LEDPAS Masks',
            'short_name':'lndcsm',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':7,
            'name':'FMASK',
            'short_name':'fmask',
            'description':'Landsat FMASK Derived Data Masks'
        },
        {
            'level':1,
            'name':'systematic radiometric and geometric corrected',
            'short_name':'L1G',
            'description':'Landsat Raw Imagery'
        },
        {
            'level':2,
            'name':'systematic radiometric and terrain corrected',
            'short_name':'L1T',
            'description':'Landsat Raw Imagery'
        },
        {
            'level':2,
            'name':'World View II Level 2A',
            'short_name':'LV2A-Multi',
            'description':'Landsat Raw Imagery'
        },
        {
            'level':2,
            'name':'World View II Level 2A Pan',
            'short_name':'LV2A-P',
            'description':'Landsat Raw Imagery'
        },
        {
            'level':2,
            'name':'World View II Level 2A Orthorectified',
            'short_name':'LV2A-Multi-ORTHO',
            'description':'Landsat Raw Imagery'
        },
        {
            'level':2,
            'name':'World View II Level 2A Pan Orthorectified',
            'short_name':'LV2A-P-ORTHO',
            'description':'Landsat Raw Imagery'
        },
        {
            'level':3,
            'name':'MODIS Combined BRDF Corrected Reflectances MCD43A4',
            'short_name':'MCD43A4',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Terra Surface Reflectance Bands 1-7 8 day',
            'short_name':'MOD09A1',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Terra Land Surface Temperature & Emissivity 8 day',
            'short_name':'MOD11A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Aqua Land Surface Temperature & Emissivity 8 day',
            'short_name':'MYD11A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Combined Land Cover Type yearly',
            'short_name':'MCD12Q1',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Combined Land Cover Dynamics yearly',
            'short_name':'MCD12Q2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Terra Vegetation Indices 16 day',
            'short_name':'MOD13Q1',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Aqua Vegetation Indices 16 day',
            'short_name':'MYD13Q1',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Terra Vegetation Indices 16 day',
            'short_name':'MOD13A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Aqua Vegetation Indices 16 day',
            'short_name':'MYD13A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Combined Leaf Area Index - FPAR 8 day',
            'short_name':'MCD15A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Terra Leaf Area Index - FPAR 8 day',
            'short_name':'MOD15A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Aqua Leaf Area Index - FPAR 8 day',
            'short_name':'MYD15A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Terra Gross Primary Productivity 8 day',
            'short_name':'MOD17A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Combined BRDF-Albedo Quality 16 day',
            'short_name':'MCD43A2',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Terra Vegetation Indices 16 day',
            'short_name':'MOD13A1',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Aqua Vegetation Indices 16 day',
            'short_name':'MYD13A1',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Terra Surface Reflectance Bands 1-2 8 day',
            'short_name':'MOD09Q1',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':3,
            'name':'MODIS Aqua Surface Reflectance Bands 1-7 8 day',
            'short_name':'MYD09A1',
            'description':'Landsat LEDAPS Calibrated Products'
        },
        {
            'level':1,
            'name':'systematic geometric corrected; too few GCP for orthorectification',
            'short_name':'L1GT',
            'description':'Landsat Raw Imagery'
        },
        {
            'level':3,
            'name':'spot5 top of atmosphere reflectance - georeferenced',
            'short_name':'spot5toageoref',
            'description':'SPOT 5 Georeferenced by CONABIO'
        },
        {
            'level':0,
            'name':'Corrupt Data',
            'short_name':'Corrupt',
            'description':None
        }
    ]
    
    algorithms_array = [
        {
            'name':'ImageSegmentationProcessing_Shape',
            'description':'Image segmentation processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ImadMafCommandRE',
            'description':'MADMex RapidEye Potential Change Classification.',
            'command':None,
            'is_supervised':False
        },
        {
            'name':'INEGIUSVPERSII-IV',
            'description':'Persistent polygons from INEGI USV Series II-IV.',
            'command':None,
            'is_supervised':False
        },
        {
            'name':'C5PreparationPerDate',
            'description':'C5 input files per date .names, .cases, .data.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'manualtraining',
            'description':'Manual training data generation.',
            'command':None,
            'is_supervised':False
        },
        {
            'name':'C5Preparation',
            'description':'C5 input files per footprint .names, .cases, .data.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeLCResultsStack',
            'description':'Layer stack of several classificaction results of same footprint.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeLCConfidencesStack',
            'description':'Layer stack of several classificaction confindences of same footprint.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'REClassificationCommand',
            'description':'MADMex RapidEye Landcover Classification Workflow.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LSClassificationCommand',
            'description':'MADMex Landsat Landcover Classification Workflow.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'C5ResultExportProcessing',
            'description':'C5 classification result to files processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QAInvarMask',
            'description':'Mask calculation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'SpectralIndicesLandsat',
            'description':'Spectral indices calculation based on Landsat data using masks.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'C5Classify',
            'description':'C5 classification process.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeQAWorkflow',
            'description':'RapidEye QA workflow.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ChangeDetectionRE',
            'description':'Change detection using iMAD, MAF transformation based on Landsat data.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatPreprocessing',
            'description':'Landsat preprocessing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ChangeMaskPost',
            'description':'Classification post processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'SpectralIndicesLandsatLocal',
            'description':'Spectral indices calculation based on Landsat data using masks.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QADatabaseDecision',
            'description':'Write decision.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeReference',
            'description':'Rapideye reference image creation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatDisturbanceWorkflow',
            'description':'Landsat disturbance workflow.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeLccWorkflowV2',
            'description':'RapidEye LCC workflow Version 2.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'WarpImageToReference',
            'description':'Warp image to reference.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ClassificationPostProcessing',
            'description':'Classification post processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QARasterOverlap',
            'description':'Image acquisition retrieval.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QACrossCorrelation',
            'description':'Cross correlation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeStacking',
            'description':'Image acquisition retrieval.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LegendIngestion',
            'description':'Legend ingestion.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ProductIngestion',
            'description':'Data ingestion.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatSegmentsModelling',
            'description':'Landsat feature modelling package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyePreprocessing',
            'description':'RapidEye preprocessing packages.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatChip4Humedas',
            'description':'Landsat chipping.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ChangeDetectionLS',
            'description':'Change detection using imad maf transformation based on Landsat data.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QAXY2PhiR',
            'description':'Convert cartesian coordinates to polar coordinates.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'MallaCreation',
            'description':'RapidEye QA workflow.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatLccWorkflowV2',
            'description':'Landsat LCC workflow version 2.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'WorldViewImageSegmentationWorkflow',
            'description':'Image segmentation workflow.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QADatabaseUpload',
            'description':'Write statistics.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeSpectralIndices',
            'description':'Spectral indices.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ImageAcquisitionsProcess',
            'description':'Image acquisition retrieval.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ImadMafTransformationLandsat',
            'description':'Change Detection.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QAImageStatistics',
            'description':'Image statistics.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatPreProcessingWorkflow',
            'description':'Landsat LCC workflow.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatFmaskComposite',
            'description':'Landsat FMask Composite.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatSegmentsFeatureProcessingV2',
            'description':'Landsat feature processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'SegmentationStatistics',
            'description':'Segmentation statistics.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'burntArea',
            'description':'Burnt area.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatSegmentsFeatureProcessing',
            'description':'Landsat segmentation objects to database and feature'
            ' processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'Ingestion',
            'description':'Data ingestion.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatLccPostprocessWorkflow',
            'description':'Landsat LCC Post-processing workflow.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'NDVI',
            'description':'NDVI calculation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'C5ResultDatabaseProcessing',
            'description':'C5 classification result to database processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeClouds',
            'description':'Rapideye Cloud detection.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ImadMafTransformation',
            'description':'Change Detection.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'MafClassification',
            'description':'Classification of MAF components.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeLccWorkflow_EqualDates',
            'description':'RapidEye LCC workflow Version 2.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ImageSegmentationProcessing',
            'description':'Image segmentation processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ChangeLandcoverHistograms',
            'description':'classification post processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'RapidEyeSegmentsFeatureProcessing',
            'description':'Rapidye feature processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QADatabaseExtraction',
            'description':'Image acquisition retrieval.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'MafTransformation',
            'description':'Change Detection.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ImageAcquisitionsSortByDateProcess',
            'description':'Image acquisition retrieval.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'MadTransformation',
            'description':'Change Detection.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ImageMasking',
            'description':'Mask image based on separate mask image defined with masking values.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'PostProcessing',
            'description':'classification post processing package.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'QADecision',
            'description':'Image statistics.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'TemporalMetrics',
            'description':'Temporal features.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatChange',
            'description':'Landsat change.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'EVI',
            'description':'EVI calculation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'ARVI',
            'description':'ARVI calculation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LAI',
            'description':'LAI calculation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'GNVI',
            'description':'GNVI calculation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'GI',
            'description':'GI calculation.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'SinusAngle2D',
            'description':'Calculates sinus of 2D angle.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'CosinusAngle2D',
            'description':'Calculates cosinus of 2D angle.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'Spot5Georef_ChangeDetection',
            'description':'Change detection using MAD, MAF and vectorization based on SPOT data.',
            'command':None,
            'is_supervised':True
        },
        {
            'name':'LandsatLccWorkflowOli',
            'description':'Landsat8 LCC workflow version 2.',
            'command':None,
            'is_supervised':True
        },
    ]
    satellites_array = [
        {
            'short_name':'RE1',
            'name':'RapidEye 1 (Tachys)',
            'sensor':'RE',
            'organization':'BlackBridge'
        },
        {
            'short_name':'RE2',
            'name':'RapidEye 2 (Mati)',
            'sensor':'RE',
            'organization':'BlackBridge'
        },
        {
            'short_name':'RE3',
            'name':'RapidEye 3 (Choma)',
            'sensor':'RE',
            'organization':'BlackBridge'
        },
        {
            'short_name':'RE4',
            'name':'RapidEye 4 (Choros)',
            'sensor':'RE',
            'organization':'BlackBridge'},
        {
            'short_name':'RE5',
            'name':'RapidEye 5 (Trochia)',
            'sensor':'RE',
            'organization':'BlackBridge'
        },
        {
            'short_name':'SPOT-5',
            'name':'SPOT 5',
            'sensor':'SPOT-5',
            'organization':'Spot Image'
        },
        {
            'short_name':'SPOT-6',
            'name':'SPOT-6',
            'sensor':'SPOT-6',
            'organization':'Spot Image'
        },
        {
            'short_name':'LS-4',
            'name':'Landsat 4',
            'sensor':'TM',
            'organization':'NASA'
        },
        {
            'short_name':'LS-5',
            'name':'Landsat 5',
            'sensor':'TM',
            'organization':'NASA'
        },
        {
            'short_name':'LS-6',
            'name':'Landsat 6',
            'sensor':'ETM+',
            'organization':'NASA'
        },
        {
            'short_name':'LS-7',
            'name':'Landsat 7',
            'sensor':'ETM+',
            'organization':'NASA'
        },
        {
            'short_name':'LS-8',
            'name':'Landsat 8',
            'sensor':'OLI_TIRS',
            'organization':'NASA'
        },
        {
            'short_name':'Terra',
            'name':'Terra (EOS AM)',
            'sensor':'MODIS',
            'organization':'NASA'
        },
        {
            'short_name':'Aqua',
            'name':'Aqua (EOS PM)',
            'sensor':'MODIS',
            'organization':'NASA'
        },
        {
            'short_name':'P6',
            'name':'ResourceSat-1',
            'sensor':'IRS-P6',
            'organization':'ISRO'
        },
        {
            'short_name':'WV02',
            'name':'WV02',
            'sensor':'WV02',
            'organization':'Digital Globe'
        },
    ]
    bands_array = [
        {
            'sensor':'RE',
            'unit':'micrometer',
            'bit_depth':0,
            'band':1,
            'minimum_wavelength':0.44,
            'maximum_wavelength':0.51
        },
        {
            'sensor':'RE',
            'unit':'micrometer',
            'bit_depth':0,
            'band':2,
            'minimum_wavelength':0.52,
            'maximum_wavelength':0.59
        },
        {
            'sensor':'RE',
            'unit':'micrometer',
            'bit_depth':0,
            'band':3,
            'minimum_wavelength':0.63,
            'maximum_wavelength':0.685
        },
        {
            'sensor':'RE',
            'unit':'micrometer',
            'bit_depth':0,
            'band':4,
            'minimum_wavelength':0.69,
            'maximum_wavelength':0.73
        },
        {
            'sensor':'RE',
            'unit':'micrometer',
            'bit_depth':0,
            'band':5,
            'minimum_wavelength':0.76,
            'maximum_wavelength':0.85
        },
        {
            'sensor':'SPOT-5',
            'unit':'micrometer',
            'bit_depth':0,
            'band':1,
            'minimum_wavelength':0.5,
            'maximum_wavelength':0.59
        },
        {
            'sensor':'SPOT-5',
            'unit':'micrometer',
            'bit_depth':0,
            'band':2,
            'minimum_wavelength':0.61,
            'maximum_wavelength':0.68
        },
        {
            'sensor':'SPOT-5',
            'unit':'micrometer',
            'bit_depth':0,
            'band':3,
            'minimum_wavelength':0.78,
            'maximum_wavelength':0.8
        },
        {
            'sensor':'SPOT-5',
            'unit':'micrometer',
            'bit_depth':0,
            'band':4,
            'minimum_wavelength':1.58,
            'maximum_wavelength':1.75
        },
        {
            'sensor':'SPOT-5-P',
            'unit':'micrometer',
            'bit_depth':0,
            'band':1,
            'minimum_wavelength':0.48,
            'maximum_wavelength':0.71
        },
        {
            'sensor':'TM',
            'unit':'micrometer',
            'bit_depth':0,
            'band':1,
            'minimum_wavelength':0.45,
            'maximum_wavelength':0.52
        },
        {
            'sensor':'TM',
            'unit':'micrometer',
            'bit_depth':0,
            'band':2,
            'minimum_wavelength':0.52,
            'maximum_wavelength':0.6
        },
        {
            'sensor':'TM',
            'unit':'micrometer',
            'bit_depth':0,
            'band':3,
            'minimum_wavelength':0.63,
            'maximum_wavelength':0.69
        },
        {
            'sensor':'TM',
            'unit':'micrometer',
            'bit_depth':0,
            'band':4,
            'minimum_wavelength':0.76,
            'maximum_wavelength':0.9
        },
        {
            'sensor':'TM',
            'unit':'micrometer',
            'bit_depth':0,
            'band':5,
            'minimum_wavelength':1.55,
            'maximum_wavelength':1.75
        },
        {
            'sensor':'TM',
            'unit':'micrometer',
            'bit_depth':0,
            'band':6,
            'minimum_wavelength':10.4,
            'maximum_wavelength':12.5
        },
        {
            'sensor':'TM',
            'unit':'micrometer',
            'bit_depth':0,
            'band':7,
            'minimum_wavelength':2.08,
            'maximum_wavelength':2.35
        },
        {
            'sensor':'ETM+',
            'unit':'micrometer',
            'bit_depth':0,
            'band':1,
            'minimum_wavelength':0.45,
            'maximum_wavelength':0.515
        },
        {
            'sensor':'ETM+',
            'unit':'micrometer',
            'bit_depth':0,
            'band':2,
            'minimum_wavelength':0.525,
            'maximum_wavelength':0.605
        },
        {
            'sensor':'ETM+',
            'unit':'micrometer',
            'bit_depth':0,
            'band':3,
            'minimum_wavelength':0.63,
            'maximum_wavelength':0.69
        },
        {
            'sensor':'ETM+',
            'unit':'micrometer',
            'bit_depth':0,
            'band':4,
            'minimum_wavelength':0.75,
            'maximum_wavelength':0.9
        },
        {
            'sensor':'ETM+',
            'unit':'micrometer',
            'bit_depth':0,
            'band':5,
            'minimum_wavelength':1.55,
            'maximum_wavelength':1.75
        },
        {
            'sensor':'ETM+',
            'unit':'micrometer',
            'bit_depth':0,
            'band':6,
            'minimum_wavelength':10.4,
            'maximum_wavelength':12.5
        },
        {
            'sensor':'ETM+',
            'unit':'micrometer',
            'bit_depth':0,
            'band':7,
            'minimum_wavelength':2.09,
            'maximum_wavelength':2.35
        },
        {
            'sensor':'ETM+',
            'unit':'micrometer',
            'bit_depth':0,
            'band':8,
            'minimum_wavelength':0.52,
            'maximum_wavelength':0.9
        },
    ]
    hosts_array = [
        {
            'hostname':'172.17.0.2',
            'alias':'MADMEX_CONTAINER',
            'user':'root',
            'password':'madmex',
            'port':'22',
            'configuration':'CONABIO'
        },
        {
            'hostname':'96.126.98.33',
            'alias':'LINODE_CONTAINER',
            'user':'root',
            'password':'J*1n!d_$W0',
            'port':'22',
            'configuration':'LINODE'         
        },
    ]
    commands_array = [
         {
            'hostname':'172.17.0.2',
            'command':'ingest',
            'queue':'workers.q'
        },
        {
            'hostname':'96.126.98.33',
            'command':'greet',
            'queue':'workers.q'        
        },
    ]
    units = [Unit(
        name=x['name'],
        unit=x['unit']) for x in units_array]
    session.add_all(units)
    organizations = [Organization(
        name=x['name'],
        description=x['description'],
        country=x['country'],
        url=x['url']) for x in organizations_array]
    session.add_all(organizations)
    sensors = [Sensor(
        name=x['name'],
        reference_name=x['reference_name'],
        description=x['description']) for x in sensors_array]
    session.add_all(sensors)
    legends = [Legend(
        name=x['name'],
        styled_layer_descriptor=x['styled_layer_descriptor']) for x in legends_array]
    session.add_all(legends)
    algorithms = [Algorithm(
        name=x['name'],
        description=x['description'],
        command=x['command'],
        is_supervised=x['is_supervised']) for x in algorithms_array]
    session.add_all(algorithms)
    satellites = [Satellite(
        name=x['name'],
        short_name=x['short_name'],
        organization=session.query(Organization).filter(
            Organization.name == x['organization']).first()) for x in satellites_array]
    session.add_all(satellites)
    bands = [Band(
        band=x['band'],
        minimum_wavelength=x['minimum_wavelength'],
        maximum_wavelength=x['maximum_wavelength'],
        bit_depth=x['bit_depth'],
        sensor=session.query(Sensor).filter(Sensor.name == x['sensor']).first(),
        unit=session.query(Unit).filter(Unit.name == x['unit']).first()) for x in bands_array]
    session.add_all(bands)
    descriptions = [Description(
        description=x['description'],
        creator=session.query(Organization).filter(
            Organization.name == x['creator']).first(),
        publisher=session.query(Organization).filter(
            Organization.name == x['publisher']).first(),
         ) for x in descriptions_array]
    session.add_all(descriptions)
    product_types = [ProductType(
        level=x['level'],
        name=x['name'],
        short_name=x['short_name'],
        description=session.query(Description).filter(Description.description == x['description']).first()) for x in product_type_array]
    session.add_all(product_types)
    hosts = [Host(
        hostname=x['hostname'],
        alias=x['alias'],
        user=x['user'],
        password=x['password'],
        port=x['port'],
        configuration=x['configuration']) for x in hosts_array]
    session.add_all(hosts)
    commands = [Command(
        host=session.query(Host).filter(Host.hostname == x['hostname']).first(),
        command=x['command'],
        queue=x['queue']) for x in commands_array]
    session.add_all(commands)
    session.commit()
    session.close_all()

def create_database():
    '''
    This method creates the database model in the database engine.
    '''
    BASE.metadata.create_all(ENGINE)
def delete_database():
    '''
    This method deletes the database model in the database engine.
    '''
    BASE.metadata.drop_all(ENGINE)

# a => \u00E1
# e => \u00E9
# i => \u00ED
# o => \u00F3
# u => \u00FA


def create_vector_tables(path_query):
    klass = sessionmaker(bind=ENGINE)
    session = klass()
    file_open = open(path_query, 'r')
    sql = " ".join(file_open.readlines())
    session.execute(sql)

if __name__ == '__main__':
    CREATE = 1
    if CREATE:
        delete_database()
        print 'database deleted'
        path_query = getattr(SETTINGS, 'RAPIDEYE_FOOTPRINTS_MEXICO_OLD')
        create_vector_tables(path_query)
        print 'vector tables created'
        create_database()
        print 'database created'
        populate_database()
        print 'database populated'
    else:
        delete_database()
        print 'database deleted'
