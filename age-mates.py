import pandas as pd
import ssl
import streamlit as st
from ipyvizzu import Data, Config, Style
from ipyvizzustory import Story, Slide, Step
from streamlit.components.v1 import html

# Set the app title and configuration
st.set_page_config(page_title='My Age-Mates', layout='centered')

# Center the title using HTML and CSS
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        text-align: center;
        width: 100%;
    }
    .title {
        font-size: 2.5em;
        margin-top: 0;
        margin-bottom: 0.5em;
    }
    </style>
    <div class="centered">
        <h1 class="title">Your Age-Mates</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Fix SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Load and prepare the data
initial_csv_path = 'data.csv'  # Adjusted path for local execution
df = pd.read_csv(initial_csv_path, encoding='ISO-8859-1')

st.subheader('When and Where Were You Born?', divider='rainbow')

# Create columns for the selections
col1, col2, col3 = st.columns(3, gap="medium")

# Function to match year with generation
def get_generation(year):
    if 1946 <= year <= 1964:
        return "Baby Boomer"
    elif 1965 <= year <= 1980:
        return "Gen X"
    elif 1981 <= year <= 1996:
        return "Millennial"
    elif 1997 <= year <= 2012:
        return "Gen Z"
    else: 
        return "Gen A"

with col1:
    # Number input for year with automatic generation matching
    selected_year = st.number_input('Year Born (1950-2024)', min_value=1950, max_value=2024, value=1980)
    generation = get_generation(selected_year)

with col2:
    country_list = df['Country'].drop_duplicates()
    selected_country = st.selectbox('Country', country_list)

abr_country = df['ISO3_code'].loc[df['Country'] == selected_country].values[0]

# Determine the subregion for the selected country
subregion = df['Subregion'].loc[df['Country'] == selected_country].drop_duplicates().values[0]

continent = df['Continent'].loc[df['Country'] == selected_country].drop_duplicates().values[0]


with col3:
    gender_list = df['Gender'].drop_duplicates()
    selected_gender = st.radio('Gender', gender_list)

g_type = df['G_Type'].loc[df['Gender'] == selected_gender].values[0]




# Add new column to mark selected year
df['IsSelectedYear'] = df['Year'].apply(lambda x: 'yes' if x == selected_year else 'no')

if st.button('Create Story'):

    # Wrap the presentation in a centered div
    st.markdown('<div class="centered">', unsafe_allow_html=True)

    # Define the dimensions for the visualization
    width = 600
    height = 450
    # Initialize the ipyvizzu Data object
    vizzu_data = Data()
    df['Year2'] = df['Year']
    df['Year2'] = df['Year2'].astype(str)
    vizzu_data.add_df(df)  # Use the updated DataFrame directly

    # Initialize the story
    story = Story(data=vizzu_data)

    def format_population(population):
        if population >= 1e9:
            return f"{population / 1e9:.1f}B"
        elif population >= 1e6:
            return f"{population / 1e6:.1f}M"
        elif population >= 1e3:
            return f"{population / 1e3:.1f}K"
        else:
            return str(population)


    # Slide 1: No. of people with the same sex, born in the same year, same country
    pop1 = df[(df['Year'] == selected_year) & (df['Country'] == selected_country) & (df['Gender'] == selected_gender)]['Population'].sum()
    title1 = f"You Are One of {format_population(pop1)} {g_type} Born in {selected_year} in {abr_country}"

    # Slide 1: No. of people with the same sex, born in the same year, same country
    slide1 = Slide(
        Step(
            Data.filter(f"record['Year'] == '{selected_year}' && record['Country'] == '{selected_country}' && record['Gender'] == '{selected_gender}'"),
            Config(
                {

                    'color': 'Gender',
                    'size': 'Population',
                    'geometry': 'circle',
                    'label': 'Population',
                    'legend':None,
                    'title': title1
                }
            ),
            Style({
                'logo' : {'width' : '5em', 'filter': 'none'},
                'title' : {'fontSize' : '3em'},
                'plot' : {'marker' :{ 
                    'label' :{ 
                        'format' : 'dimensionsFirst',
                        'fontSize' : '2.5em',
                        }
                    }},
            })
        )
    )
    story.add_slide(slide1)

    pop2 = df[(df['Year'] == selected_year) & (df['Country'] == selected_country)]['Population'].sum()
    title2 = f"You Are One of {format_population(pop2)} People Born in {selected_year} in {abr_country}"

    slide2 = Slide(
        Step(
            Data.filter(f"record['Country'] == '{selected_country}' && record['Year'] == '{selected_year}'"),
            Config(
                {
                    'label': ['G_Type','Population'],
                    'title': title2
                }
            ),
            Style({
                'plot' : {'marker' :{ 
                    'label' :{ 
                        'fontSize' : '1.8em',
                        }
                    }},
            })
        )
    )
    story.add_slide(slide2)

    pop3 = df[(df['Subregion'] == subregion) & (df['Year'] == selected_year)]['Population'].sum()
    title3 = f"You Are One of {format_population(pop3)} People Born in {selected_year} in {subregion}"

    slide3 = Slide()
    slide3.add_step(
        Step(
            Data.filter(f"record['Subregion'] == '{subregion}' && record['Year'] == {selected_year}"),
            Config(
                {
                    'color': 'Country',
                    'label': ['ISO3_code', 'Population'],
                    'legend': None,
                    'title': title3
                }
            ),
            Style({
                 "plot": {
                "marker": {
                    "label": {
                        "numberFormat": "prefixed",
                        "maxFractionDigits": "1",
                        "numberScale": "shortScaleSymbolUS",
                    },
                },
            }
            })
        )
    )
    story.add_slide(slide3)

    pop4 = df[(df['Continent'] == continent) & (df['Year'] == selected_year)]['Population'].sum()
    title4 = f"You are One of {format_population(pop4)} People Born in {selected_year} in {continent}"

    slide4 = Slide()
    slide4.add_step(
        Step(
            Data.filter(f"record['Continent'] == '{continent}' && record['Year'] == {selected_year}"),
            Config(
                {
                    'title': title4,
                    'size':['Population'],
                }
            )
        )
    )
    story.add_slide(slide4)

    pop5 = df[(df['Year'] == selected_year)]['Population'].sum()
    title5 = f"You Are One of {format_population(pop5)} People Born in {selected_year} in the World"

    slide5 = Slide(
        Step(
            Data.filter(f"record['Year'] == '{selected_year}'"),
            Config(
                {
                    'color': 'Continent',
                    'label': ['Continent', 'Population'],
                    'title': title5
                }
            )
        )
    )
    story.add_slide(slide5)

    slide6 = Slide()

    slide6.add_step(
        Step(
            Data.filter(f"record['Year'] == '{selected_year}'"),
            Config(
                {
                    'geometry': 'rectangle',
                    'x': 'Year2',
                    'y': ['Population','Continent'],
                    'label': None,
                    'title': title5
                }
            )
        )
    )

    slide6.add_step(
        Step(
            Config(
                {
                    'y': 'Population',
                    'color': 'Generation',
                }
            )
        )
    )

    
    slide6.add_step(
        Step(
            Config(
                {
                    'label': 'Population',
                }
            )
        )
    )

    pop6 = df[(df['Generation'] == generation)]['Population'].sum()
    title6 = f"You Belong to the {format_population(pop6)} {generation}s Worldwide"

    slide6.add_step(
        Step(
            Data.filter(f"record['Generation'] == '{generation}'"),
            Config(
                {
                    'title': title6
                }
            )
        )
    )
    story.add_slide(slide6)

    slide7 = Slide()

    slide7.add_step(
        Step(
            Config(
                {
                    'label': None,
                }
            )
        )
    )

    slide7.add_step(
        Step(
            Config(
                {
                    'x': ['Generation','Population'],
                    'y': None
                }
            )
        )
    )

    slide7.add_step(
        Step(
            Config(
                {
                    'label':'Population'                        
                }
            ),
            Style({
                'plot' : {'marker' :{ 'label' :{ 'position' : 'center'}}},
            })
        )
    )

    pop7 = df['Population'].sum()

    slide7.add_step(
        Step(
                Data.filter(None),
                Config(
                    {
                        'label':['Generation','Population'],
                        'title': f"You Are One of {format_population(pop7)} People Born after 1950 in the World"
                    }
                )
        )
    )

    story.add_slide(slide7)

    slide8 = Slide()

    slide8.add_step(
        Step(
                Data.filter(None),
                Config(
                    {
                        'label':['Generation','Population'],
                        'align':'stretch',
                        'title': f"Your Generation is {(pop6 / pop7) * 100:.1f}% of People Born after 1950"
                    }
                )
        )
    )

    story.add_slide(slide8)

    slide9 = Slide()

    slide9.add_step(
        Step(
                Data.filter(None),
                Config(
                    {
                        'label':None,
                        'x':['Year2','Generation','Population'],
                        'title': f"You and Your {format_population(pop5)} Age-Mates Are {(pop5 / pop7) * 100:.1f}% of People Born after 1950"
                    }
                )
        )
    )

    story.add_slide(slide9)

 
    story.start_slide = 6

    # Switch on the tooltip that appears when the user hovers the mouse over a chart element.
    story.set_feature('tooltip', True)

    html(story._repr_html_(), width=width, height=height)

    st.download_button('Download HTML export', story.to_html(), file_name=f'demographics-{selected_country}.html', mime='text/html')

    # Close the centered div
    st.markdown('</div>', unsafe_allow_html=True)
