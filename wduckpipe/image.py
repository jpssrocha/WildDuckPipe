""""
Biblioteca com funções relacionadas a redução imagens astronômicas em grande 
quantidade seguindo o padrão adotado na missão de observação OI2018B-011 do
OPD/LNA.

TODO: 
    Melhorar descrição das funções.
    Testar e debugar função align_and_combine().
    Implementar função de astrometria.

  Atualizações: 

        26-04-2019 : Implementada primeira versão da função align_and_combine()
        27-04-2019 : Função mkdirs_list adaptada para remover espaços
                     Reimplementação de align_and_combine usando astroalign
        27-05-2019: Consertando erro gerado pela remoção de espaços em mkdirs_list()

"""
import matplotlib.pyplot as plt
import numpy as np
import os
from glob import glob
from astropy.io import fits
from datetime import datetime as dt
import astroalign

# 1. Funções para lidar com movimentação e organização de arquivos


def move_files(arquivos, destino):
    """"
    Move lista de arquivos para o destino especificado
    """
    quantidade = len(arquivos)
    print("Movendo", quantidade, "arquivos... \n")
    i = 1
    for arquivo in arquivos:
        print("%s ====> %s/%s (%i de %i)" %
                (arquivo, destino, arquivo, i, quantidade))
        os.rename(arquivo, destino + "/" + arquivo)
        i+=1
    print("\n")

def get_headers_cwd():
    """"
    Retorna cabeçalhos dos arquivos na pasta atual
    """
    files = glob("*.fits")
    headers = [fits.getheader(file) for  file in files]
    return headers

def mkdirs_list(list_of_directories):
    """"
    Cria lista de diretórios e dá feedback do progresso
    """
    for i in list_of_directories:
        print("Criando diretório:", i)
        os.makedirs(i)
    print("\n")


def select_images(keyword, value):
    """"
    Seleciona arquivos da coleção de cabeçalhos baseados numa chave e valor
    """
    files = glob("*.fits")
    headers = get_headers_cwd()
    return [j for i,j in zip(headers,files) if i[keyword]==value]

def select_images_CommentFormat(keyword, value):
    """"
    Seleciona arquivos da coleção de cabeçalhos baseados numa chave e valor
    """
    headers = get_headers_cwd()
    return [i["IMAGE"]+".fits" for i in headers if i[keyword][0].split("'")[1].strip()==value]

def sep_by_object(folder = "./"):
    """"
    Separa os arquivos fits em uma pasta de acordo com o objeto observado
    """
    current_folder = os.getcwd() #Recording the present folder to return later
    os.chdir(folder)
    
    headers = get_headers_cwd()
    objcts = set([obj["OBJECT"] for obj in headers]) #Creating set of objects
    
    print(objcts)

    mkdirs_list(objcts)
    
    for obj in objcts:
        move_files(select_images("OBJECT",obj), obj)
        headers = get_headers_cwd()
        
    os.chdir(current_folder)

def sep_by_filter(folder = "./"):
    """"
    Separa arquivos em uma pasta de acordo com o filtro
    """
    current_folder = os.getcwd() 
    os.chdir(folder)
    
    headers = get_headers_cwd()
    filters = set([obj["FILTER"] for obj in headers])
    
    print("Imagens nos filtros:\t", filters, "\n")
    # Creating directories
    mkdirs_list(filters)
    
    for f in filters:
        move_files(select_images("FILTER",f), f)
        headers = get_headers_cwd()
        
    os.chdir(current_folder)
    
def sep_object_by_filter(folder = "./"):
    """
    Dado caminho relativo para uma pasta cuja as sub-pastas são de objetos,
    separa as imagens dos objetos por filtro
    """
    
    current_folder = os.getcwd() 
    os.chdir(folder)
    
    objects_folder_list = os.listdir()
    
    for folder in objects_folder_list:
        print("Organizando imagens de ", folder, "\n")
        sep_by_filter(folder)
        print("\n")
    
    os.chdir(current_folder)

def sep_by_exptime(folder = "./"):
    """"
    Separa arquivos em uma pasta de acordo com o filtro
    """
    current_folder = os.getcwd() 
    os.chdir(folder)
    
    headers = get_headers_cwd()
    exptimes = set([obj["EXPTIME"].split(",")[0] for obj in headers])
    
    print("Imagens nos tempos de exposição:\t", exptimes, "\n")
    # Creating directories
    mkdirs_list(filters)
    
    for expt in exptimes:
        move_files(select_images("EXPTIME",expt), expt)
        headers = get_headers_cwd()
        
    os.chdir(current_folder)


def imstat(fits_file):
    """"
    Printa em tela e retorna estatísticas da imagem em um dicionário
    """
    image = fits.getdata(fits_file)
    print("Imagem: %s" % (fits_file))
    print("Mediana: " + str(np.median(image)) + " contagens")
    print("Média: " + str(np.mean(image)) + " contagens")
    print("Std: " + str(np.std(image)) + " contagens")   
    print("Max: " + str(np.max(image)) + " contagens")
    print("Min: " + str(np.min(image)) + " contagens")
    print("\n")
    
    return {"median":np.median(image), 
            "mean":np.mean(image), 
            "std":np.std(image),
            "max":np.max(image),
            "min":np.min(image)
           }

def make_MasterBias(bias_folder, out_folder):
    """"
    Dado o caminho relativo a pasta com os bias gera master bias e salva no caminho relativo especificado
    """
    current_folder = os.getcwd() 
    os.chdir(bias_folder)
    
    out = out_folder+"master_bias.fits"
    files = os.listdir()
    ref_header = fits.getheader(files[0])
    NCOMBINE = len(files)
    
    print("Carregando e empilhando %i imagens ... \n" % (NCOMBINE))
    bias_cube = np.stack([fits.getdata(image) for image in files],axis=0)
    
    print("Extraindo medianas ... \n")
    master_bias = np.median(bias_cube, axis=0)

    # Escrevendo meta-dados no cabeçalho
    now = dt.now().strftime("%B %d, %Y")
    ref_header["NCOMBINE"] = NCOMBINE
    ref_header["MASTER_BIAS"] = "Done. %s" % (now)
    
    print("Escrevendo FITS ... \n")
    fits.writeto(out, master_bias, ref_header)
    
    print("Gerado master bias: %s \n Estatistica de contagens: \n" % out)
    imstat(out)
    
    os.chdir(current_folder)
    
    return out

def make_MasterFlat(flat_folder, out_folder, master_bias):
    """"
    Dada localização relativa da pasta de flats e o master bias, gera arquivos de flat master
    """
    current_folder = os.getcwd() 
    os.chdir(flat_folder)
    
    files = os.listdir()
    ref_header = fits.getheader(files[0])
    band = ref_header["FILTER"]
    
    master_bias = fits.getdata(master_bias)
    NCOMBINE = len(files)
    
    flat_cube = np.stack([fits.getdata(image) for image in files],axis=0)
    
    master_flat = np.median(flat_cube, axis=0) - master_bias
    
    mean = np.mean(master_flat)
    
    norm_master_flat = master_flat / mean
    
    file_name = out_folder + "master_flat_%s.fits" % (band)

    # Escrevendo meta-dados no cabeçalho
    now = dt.now().strftime("%B %d, %Y")
    ref_header["NCOMBINE"] = NCOMBINE
    ref_header["MASTER_FLAT"] = "Done. %s" % (now)
    
    fits.writeto(file_name, norm_master_flat, ref_header)
    
    imstat(file_name)
    
    os.chdir(current_folder)
    
    return file_name
    
def make_MasterFlat_all(flats_folder, out_folder, master_bias):
    """
    Dado caminho relativo da pasta de flats aplica função de master flat para cada filtro 
    (dado que foram separados em pastas)
    """
    
    current_folder = os.getcwd()
    
    os.chdir(flats_folder)
    sub_folders = os.listdir()
    
    mflat_dict = {}
    
    for folder in sub_folders:
        mflat_dict[folder] = make_MasterFlat(folder, out_folder, master_bias)
        print("\n")
        
    os.chdir(current_folder)
    
    return mflat_dict
    
def ccdproc(image_file, out_path, master_bias, master_flat):
    """"
    Dado caminho para imagem de determinado objeto em
    determinado filtro aplica imagens de calibração
    """
    mbias = fits.getdata(master_bias)
    mflat = fits.getdata(master_flat)
    
    header = fits.getheader(image_file)
    image = fits.getdata(image_file)
    
    print("Processando imagem: %s ..." % (image_file) )
    
    proc_image = (image - mbias) / mflat
    
    out = out_path + "r_%s" % (image_file)
    
    #Updating header
    
    now = dt.now().strftime("%B %d, %Y")
    
    header["CCDProc"] = "Done: %s" % (now)
    
    fits.writeto(out, proc_image, header)

def ccdproc_all(folder_path, out_path, master_bias, master_flat):
    """"
    Dado caminho para imagem de determinado objeto em
    determinado filtro aplica imagens de calibração indicadas
    para bias e no dicionário de flats.
    """
     
    current_folder = os.getcwd() 
    os.chdir(folder_path)     
    
    images = os.listdir()
    images.sort()
    
    ref_header = fits.getheader(images[0])
    band = ref_header["FILTER"]
    
    
    N = len(images)
    
    print("Processando %i imagens no filtro %s" % (N, band))
    
    for image in images:
        ccdproc(image, out_path, master_bias, master_flat)
        
    os.chdir(current_folder)

def ccdproc_all_filters(folder_path, out_path, master_bias, master_flat_dict):
    
    current_folder = os.getcwd() 
    os.chdir(folder_path)  
    
    filters = os.listdir()
    
    for band in filters:
        master_flat = master_flat_dict[band]
        ccdproc_all(band, out_path, master_bias, master_flat)
        print("\n")
        
    os.chdir(current_folder)


def initial_reduction(observation_folder = "./"):
    """"
    Organiza arquivos de observações em pasta, levando em consideração informações do header no padrão do LNA.
    Dado caminho relativo da pasta.
    """
    
    os.chdir(observation_folder)
    
    # Definindo nomes das pastas para estrutura de arquivos (referente a pasta atual)
    root = os.getcwd()
    bias_folder = root + "/calibration/bias"
    flat_folder = root + "/calibration/flat"
    master_folder = root +"/calibration/master/"
    others_folder = root +"/others"
    raw_science_folder = root + "/science/raw"
    reduced_science_folder = root + "/science/reduced/"
    
    folders_list = [bias_folder, flat_folder, master_folder, others_folder, raw_science_folder, reduced_science_folder]
    
    # Depois de definida a estrutura de pastas podemos cria-las
    
    print("Criando estrutura de pastas ... \n")
    
    mkdirs_list(folders_list)
    
    # Agora vamos olhar os arquivos dentro da pasta e organizar as imagens de calibração (bias e flat)
    
    headers = get_headers_cwd()
    N = len(headers)
    
    bias_images = select_images("OBJECT", "bias")
    flat_images = select_images("OBJECT", "flat")
    
    print("Organizando arquivos de calibração ... \n")
    
    move_files(bias_images, bias_folder)
    move_files(flat_images, flat_folder)
    
    print("Separando flats por filtro ... \n")
    
    sep_by_filter(flat_folder)
    
    # Seguimos agora organizando o resto das imagens em duas categorias (science e others)
    # Atualizando a seleção de imagens
    
    headers = get_headers_cwd()
    
    science_images = [i["IMAGE"]+".fits" for i in headers
            if i["COMMENT"][0].split("'")[1].strip()=="science"]
    other_images = [i["IMAGE"]+".fits" for i in headers
            if i["COMMENT"][0].split("'")[1].strip()!="science"]
    
    # A função select_images() não funciona nesse caso devido a formatação 
    # do comentário no cabeçalho e a expressão !=.
    # No futuro posso deixa-la mais robusta

    # Continuando com a organização ...
    
    print("Organizando imagens de ciência e outras ... \n")
    
    move_files(science_images, raw_science_folder)
    move_files(other_images, others_folder)
    
    print("Separando imagens por objeto ... \n")
    
    sep_by_object(raw_science_folder)
    sep_by_object(others_folder)
    
    print("Separando imagens de ciência dos objetos em filtros ... \n")
    
    sep_object_by_filter(raw_science_folder)
    
    # Agora estamos com todos os arquivos organizados, vamos seguir gerando os arquivos de calibração.
    
    print("Gerando arquivos de calibração ... \n")
    
    print("Gerando Master Bias ... \n")
    
    mbias = make_MasterBias(bias_folder, master_folder)
    
    # A função make_MasterBias() imprime em tela uma boa quantidade de feedback a cada passo para termos noção
    # de quanto tempo cada passo da função está demorando para rodar.
    
    print("Gerando Master Flats ... \n")
    
    mflat_dict = make_MasterFlat_all(flat_folder, master_folder, mbias) 
    
    # Agora que temos as imagens de calibração vamos seguir calibrando as imagens de ciência
    
    # Vamos para a pasta de imagens de ciência para ver o que temos
    
    print("Aplicando arquivos de calibração nas imagens de ciência ... \n ")
    
    os.chdir(raw_science_folder)
    objcts = os.listdir()
    
    for objct in objcts:
        print("Aplicando calibrações para %s ... \n" % objct)
        ccdproc_all_filters(objct, reduced_science_folder, mbias, mflat_dict)
        
    os.chdir(root)
    
    # Imagens agora processadas na pasta de imagens reduzidas, por simplicidade elas foram salvas
    # todas juntas, agora vamos separa-las novamente.
    
    print("Fazendo organização dos arquivos reduzidos ..")
    
    sep_by_object(reduced_science_folder)
    sep_object_by_filter(reduced_science_folder)
    
    # Finalmente as imagens estão organizadas e corrigidas para erros instrumentais.

    os.chdir(root)
    
    print("Redução conluída. Foram processados %i arquivos fits." % (N))
    

def align_and_combine(folder, zero_shift, sequence_len, symmetrical = True):
    """
    Dado caminho a pasta com imagens e o nome da imagem de referência para alinhamento
    combina as imagens levando em consideração número de exposições simétrico passando
    o tamanho das sequencias de imagens.
    """

    current_folder = os.getcwd() 
    os.chdir(folder)

    images = os.listdir()
    images.sort()
    N = len(images)

    images_data = {}
    for image in images:
        images_data[image] = fits.getdata(image)

    print("Imagem de Referência : ", zero_shift)

    aligned_images = ["a"+i for i in images]

    print("Alinhando %i imagens ..." % N)

    aligned_data = {}
    for original,shifted in zip(images, aligned_images):
        print("Alinhando imagem:", original)
        aligned_data[shifted] = astroalign.register(images_data[original], images_data[zero_shift])

    print("Imagens alinhadas com sucesso !!!")

    # Combinações

    if symmetrical:
        print("Combinando imagens como sequencias simétricas")
        bin_quantity = int(len(images)/sequence_len) # Bins simétricas
        print("Tamanho das sequências: %i, Quantidade de sequencias: %i" %
                (sequence_len, bin_quantity))
        divisions = [sequence_len for i in range(sequence_len)]
        bins = {}
        register1 = 0
        register2 = divisions[0]

        for bin in range(bin_quantity):
            bins[bin] = []
            for i in range(register1, register2):
                bins[bin].append(aligned_images[i])
            register1 = register2
            register2 += divisions[bin]

    
    for bin in bins:
        ref_image = bins[bin][0].replace("a","")
        ref_header = fits.getheader(ref_image)

        NCOMBINE = len(bins[bin])

        bin_images = bins[bin]

        ref_header["NCOMBINE"] = NCOMBINE

        cube = np.stack([aligned_data[i] for i in bin_images], axis = 0)
        print("Combinando imagens pela mediana ...\n")
        final = np.median(cube, axis = 0)
        print(bins[bin])
        print("\n Escrevendo imagem final", bin)
        print("...\n")

        fits.writeto("final%i.fits" % (bin), final, ref_header) 

    print("Imagens Combinadas com Sucesso !!!")
