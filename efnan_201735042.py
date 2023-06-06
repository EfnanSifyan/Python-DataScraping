from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

#Buraya kadar olan kodlarda gerekli kütüphaneleri import ettik.

def scraping():#Burada veri kazıma işlemini arayüze almak için bir fonksiyona alıyoruz.
    tk.messagebox.showinfo(message='Receiving your data please wait')#Arayüz başladığında çıkan mesaj.
def scraping():
    start_time = time.time()  # Veri kazımı başlangıç zamanını kaydedin

    ayarlar = webdriver.ChromeOptions()
    ayarlar.add_argument("headless")#Bu kısımda otomasyonu gizliyoruz.(tarayıcı penceresi görüntülenmez ve arka planda otomatik olarak çalışır.)
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = ayarlar)
    #Buraya kadar olan kodlarda chrome'u ayarlıyoruz.
    browser.get("https://dergipark.org.tr/tr/")#Veri kazıma işlemi yapılacak siteyi alıyoruz.
    browser.maximize_window()

    search=browser.find_element(By.XPATH,("//*[@id='search_term']"))#Arama yapılacak çubuğun xpath'ini alıyoruz.
    button=browser.find_element(By.XPATH,("//*[@id='home-search-btn']"))#Arama butonunun xpath'ini alıyoruz.

    word=entry.get()#Burada hakkında arama yapılacak kelimeyi arayüze girmek için bir değişkene atıyor ve arayüzle bağlantısını kuruyoruz.
    search.send_keys(word)
    button.click()#Yukarıda arama aldığım arama butonuna burada tıklatıyoruz.

    url1=f"https://dergipark.org.tr/tr/search/?q={word}&section=articles"   
    #Burada link içerisinide {word} yazarak arancak kelime alındığında otomasyonun o adrese gitmesini sağlıyoruz.
    innerHTML=requests.get(url1)
    innerHTML=innerHTML.content
    #Burada kazıma yapılacak web adresinin kaynak kodunu alarak parse ediyoruz.

    soup=BeautifulSoup(innerHTML,"lxml")
    data_list=[]
    s="1"
    while True:
        url2=f"https://dergipark.org.tr/tr/search/{s}?q={word}&section=articles"#Burada link içerisine {s} yazarak sayfalar arasında geçiş yaptırdım.
        try: 
            links=browser.find_elements(By.XPATH,("//*[@id='kt_content']/div[2]/div[2]/div[2]/div[2]/div/div/h5/a"))
        except:
            break
        #try except kısmında sırayla makalelerin linkelerini aldırdık.
        liste=[]
        
        for link in links:
            liste.append(link.get_attribute("href")) # linklerin href özelliğini alarak links listesine URL olarak eklendi
        #Buraya kadar liste adında bir liste oluşturup aldığım makale linklerini listeledim.
        if len(liste)==0:
            break
        #Burada eğer alınacak link kalmadıysa döngü sonlanıyor ve uygulama data.xlsx adında excel oluşturuyor.
        for i in liste:
            browser.get(i)
            try:
                
                url = i
                source = requests.get(i)
                source = source.content
                soup = BeautifulSoup(source, "lxml")
                title = soup.find("h3", class_="article-title").text
                span = soup.find("span", class_="article-subtitle")
                year = span.find("a").text
                p = soup.find("p", class_="article-authors") 
                authors=p.find_all("a")
                yazar = []
                duzeltilmis_yazarlar = []
                for author in authors:

                    yazar.append(author.text)
                    for yazar1 in yazar:
                        duzeltilmis_yazar = ' '.join(yazar1.split()).strip()  # Fazla boşlukları kaldırarak tek bir boşluk bırakın
                        duzeltilmis_yazarlar.append(duzeltilmis_yazar)
                        duzeltilmis_liste = list(set(duzeltilmis_yazarlar))   # yinelenen yazar isimleri bir kez olucak şekilde düzenlendi
            #Bu kısma kadar makalelerin başlıkları,yazarları ve yazıldığı tarıhler alınıyor.
               
            
                    data={"Title":title.strip(),"Author":duzeltilmis_liste,"Year":year,"Link":url}
                data_list.append(data)
                #Burada alınan veriler data_list adında bir listede toplanıyor.
            except:
                break
    end_time = time.time()  # Veri kazımı bitiş zamanı
    elapsed_time = end_time - start_time  # Geçen süre
    tk.messagebox.showinfo(message=f"Data scraping is complete.\nElapsed Time: {elapsed_time:.2f} seconds")
    
            #Alınacak makale kalmadıysa döngüden çıkılıyor.
    s = str(int(s) + 1) #mevcut sayfa numarasını temsil eden s değişkeni bir tam sayıya dönüşürüldü.s değerine +1 ekleyerek bir sonraki sayfa numarasını elde ettik.
    url2=f"https://dergipark.org.tr/tr/search/{s}?q={word}&section=articles" #url2 değişkeni s ve word yer tutucuları sayfa numarası ve arama kelimesi ile değiştirilir.
    browser.get(url2)
        #Burası sayfadaki makaleler alındıktan sonra diğer sayfaya geçmeyi sağlıyor.

    df=pd.DataFrame(data_list) #‘data_list’ adlı bir liste üzerinde DataFrame nesnesi oluşturuldu.
    df.to_excel("data.xlsx") #DataFrame nesnesi df, "data.xlsx" adlı bir Excel dosyasına aktarıldı. 
    save_path = filedialog.asksaveasfilename(defaultextension="data.xlsx")
    if save_path:
        df.to_excel(save_path)
        
    tk.messagebox.showinfo(message='Your data scraping is complete.')
    #Burası da verilerin excele basılması ve veri kazımanın bittiğine dair kod bloğudur.

root = tk.Tk() #Arayüz penceresini oluşturmak için kullanıldı.
root.title("Scraping DergiPark Articles")

label = tk.Label(root, text="Type the word you want to search")
label.pack() 

entry = tk.Entry(root, width=50) #root penceresine bir metin giriş kutusu (entry) eklendi ve genişliği ayarlandı..
entry.pack()

root.geometry("350x100") #arayüz genişliği belirlendi.
root.configure(bg='#D7C6EE')

button = tk.Button(root, text="Pull data", command=scraping) #root penceresine bir button eklendi,metin yazıldı ve scraping() fonksiyonu çağırıldı.
button.pack() #etiket pencereye yerleştirildi.

email_label = tk.Label(root, text="efnansifyanart@gmail.com", anchor="se")
email_label.pack(side="right", padx=10, pady=10)


root.mainloop() 
#Buraya kadar olan kod arayüzü temsil ediyor. Pencere kapatılana kadar programın çalışmasını sürdürür.
