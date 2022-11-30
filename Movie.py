import streamlit as st
from PIL import Image
import json
from KNNClassifier import KNearestNeighbours
from bs4 import BeautifulSoup
import requests,io
import PIL.Image
from urllib.request import urlopen

with open('./Dataset/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('./Dataset/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)

print("Data")
print(movie_titles)
def mp(name):
    import requests
    import json

    # Base url that connects us to the server where the movie info is located
    url = "https://imdb8.p.rapidapi.com/auto-complete"

    # These headers are used to authenticate your connection
    headers = {
        'x-rapidapi-host': "imdb8.p.rapidapi.com",
        'x-rapidapi-key': "3a38a7b034msh986ec990b184947p1379f3jsn1166faac17c9"
    }

    # These are my keywords I'd like to search for
    searchTerms = [name]

    # I store all the responses in a list
    responses = []

    # Here I loop through the search terms
    for x in range(len(searchTerms)):
        # Update the searchterm in the url parameters
        querystring = {"q": searchTerms[x]}

        # Query the API and save the result
        response = requests.request("GET", url, headers=headers, params=querystring)

        # Turn the json text from the response into a useful json python object
        data = json.loads(response.text)

        # Format the json to be more readable this is mostly for viewing raw
        # response data when debugging
        formattedData = json.dumps(data, indent=4)
        # Uncomment the following line to see the raw response from the api
        #   print(formattedData)

        # Load the json data into a dictionary
        dataDict = json.loads(formattedData)

        # Save the most important data in our list
        responses.append(dataDict["d"])

    # Print out the results
    for x in range(len(searchTerms)):
        #   print("\n\nSearch Term: \"" + str(searchTerms[x]) + "\"")
        for movie in responses[x]:
            # I used try/except here to keep going just incase a movie doesn't have
            # the data I'm asking for.

            try:
                print(searchTerms[0])
                if searchTerms[0] == movie["l"]:
                    #           print("Title: " + movie["l"])
                    print(movie["i"]["imageUrl"])
                    break
            except:
                pass


def movie_poster_fetcher(imdb_link):
    ## Display Movie Poster
    # print(imdb_link)
    url_data = requests.get(imdb_link)
    # print(url_data)
    # s_data = BeautifulSoup(url_data, 'html.parser')
    # print(s_data)
    # imdb_dp = s_data.find("meta", property="og:image")
    # movie_poster_link = imdb_dp.attrs['content']
    # u = urlopen(imdb_link)
    # raw_data = u.read()
    # image = PIL.Image.open(io.BytesIO(raw_data))
    # image = image.resize((158, 301), )
    image = Image.open(imdb_link)
    st.image(image, use_column_width=False)

def get_movie_info(imdb_link):
    url_data = requests.get(imdb_link).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_content = s_data.find("meta", property="og:description")
    movie_descr = imdb_content.attrs['content']
    movie_descr = str(movie_descr).split('.')
    movie_director = movie_descr[0]
    movie_cast = str(movie_descr[1]).replace('With', 'Cast: ').strip()
    movie_story = 'Story: ' + str(movie_descr[2]).strip()+'.'
    rating = s_data.find("div", class_="AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3 jkCVKJ")
    rating = str(rating).split('<div class="AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3 jkCVKJ')
    rating = str(rating[0]).replace(''' "> ''', '').replace('">', '')

    movie_rating = 'Total Rating count: '+ rating
    return movie_director,movie_cast,movie_story,movie_rating

def KNN_Movie_Recommender(test_point, k):
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    print(target)
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Print list of 10 recommendations < Change value of k for a different number >
    table = []
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2],data[i][-1]])
    print(table)
    return table

st.set_page_config(
   page_title="Movie Recommender System",
)

def run():
    st.title("Movie Recommender System")
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
    movies = [title[0] for title in movie_titles]
    category = ['--Select--', 'Movie based', 'Genre based']
    cat_op = st.selectbox('Select Recommendation Type', category)
    if cat_op == category[0]:
        st.warning('Please select Recommendation Type!!')
    elif cat_op == category[1]:
        select_movie = st.selectbox('Select movie: (Recommendation will be based on this selection)', ['--Select--'] + movies)
        # dec = st.radio("Want to Fetch Movie Poster?", ('Yes', 'No'))
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Fetching a Movie Posters will take a time."</h4>''',
        #             unsafe_allow_html=True)
        dec='No'
        if dec == 'No':
            if select_movie == '--Select--':
                st.warning('Please select Movie!!')
            else:
                no_of_reco = st.slider('Number of movies you want Recommended:', min_value=5, max_value=20, step=1)
                genres = data[movies.index(select_movie)]
                test_points = genres
                table = KNN_Movie_Recommender(test_points, no_of_reco+1)
                table.pop(0)
                c = 0
                st.success('Some of the movies from our Recommendation, have a look below')
                for movie, link, ratings in table:
                    c+=1
                    # director,cast,story,total_rat = get_movie_info(link)
                    st.markdown(f"({c})[ {movie}]({link})")
                    # st.markdown(director)
                    # st.markdown(cast)
                    # st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
        else:
            if select_movie == '--Select--':
                st.warning('Please select Movie!!')
            else:
                no_of_reco = st.slider('Number of movies you want Recommended:', min_value=5, max_value=20, step=1)
                genres = data[movies.index(select_movie)]
                test_points = genres
                table = KNN_Movie_Recommender(test_points, no_of_reco+1)
                table.pop(0)
                c = 0
                st.success('Some of the movies from our Recommendation, have a look below')
                print(table)
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    # st.image(mp(movie))
                    # movie_poster_fetcher(mp(movie))
                    print(mp(movie))
                    # director,cast,story,total_rat = get_movie_info(link)
                    # st.markdown(mp(movie))
                    # st.markdown(cast)
                    # st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
    elif cat_op == category[2]:
        sel_gen = st.multiselect('Select Genres:', genres)
        # dec = st.radio("Want to Fetch Movie Poster?", ('Yes', 'No'))
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Fetching a Movie Posters will take a time."</h4>''',
        #             unsafe_allow_html=True)
        dec = 'No'
        if dec == 'No':
            if sel_gen:
                imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('Some of the movies from our Recommendation, have a look below')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    # director,cast,story,total_rat = get_movie_info(link)
                    # st.markdown(director)
                    # st.markdown(cast)
                    # st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
        else:
            if sel_gen:
                imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('Some of the movies from our Recommendation, have a look below')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    # movie_poster_fetcher(link)
                    # director,cast,story,total_rat = get_movie_info(link)
                    # st.markdown(director)
                    # st.markdown(cast)
                    # st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
run()
