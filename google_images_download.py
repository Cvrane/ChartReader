from google_images_download import google_images_download 

response = google_images_download.googleimagesdownload() 
search_queries = ['bar plot', 'area chart', 'box plot', 'bubble chart', 'flow chart',
'line chart', 'map plot', 'network diagram', 'pareto chart', 'pie chart', 'radar plot',
'scatter plot', 'tree diagram', 'venn diagram', 'pattern bar graph'] 

def downloadimages(query): 
        chromedriver = r"C:\ProgramData\chocolatey\lib\chromedriver\tools\chromedriver.exe"
        output_dir = r"D:\Summer2020\PSUProject\download\images"
        arguments = {"keywords": query, 
                     "limit": 2000, 
                     "print_urls": True, 
                     "size": "medium",
                     "output_directory": output_dir,
                     "chromedriver": chromedriver} 

        try: 
            response.download(arguments) 
        except: 
            pass

for query in search_queries: 
    downloadimages(query) 
    print()
