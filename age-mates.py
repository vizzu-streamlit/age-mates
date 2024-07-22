import pandas as pd
import ssl
import streamlit as st
from ipyvizzu import Data, Config, Style
from ipyvizzustory import Story, Slide, Step
from streamlit.components.v1 import html

# Set the app title and configuration
st.set_page_config(page_title='My Contemporaries', layout='centered')

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
        <h1 class="title">You in the World</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Fix SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Load and prepare the data
initial_csv_path = 'data.csv'  # Adjusted path for local execution
df = pd.read_csv(initial_csv_path, encoding='ISO-8859-1')

# Create columns for the selections
col1, col2, col3 = st.columns(3)

with col1:
    country_list = df['Country'].drop_duplicates()
    selected_country = st.selectbox('Country:', country_list)

abr_country = df['ISO3_code'].loc[df['Country'] == selected_country].values[0]

# Determine the subregion for the selected country
subregion = df['Subregion'].loc[df['Country'] == selected_country].drop_duplicates().values[0]

continent = df['Continent'].loc[df['Country'] == selected_country].drop_duplicates().values[0]

with col2:
    gender_list = df['Gender'].drop_duplicates()
    selected_gender = st.radio('Gender:', gender_list)

g_type = df['G_Type'].loc[df['Gender'] == selected_gender].values[0]

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

with col3:
    # Number input for year with automatic generation matching
    selected_year = st.slider('Year Born', min_value=1950, max_value=2024, value=1980)
    generation = get_generation(selected_year)

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

    slide5_1 = Slide(
        Step(
            Data.filter(f"record['Year'] == '{selected_year}'"),
            Config(
                {
                    'geometry': 'rectangle',
                    'x': 'Year2',
                    'y': ['Population','Continent'],
                    'label': 'Population',
                    'legend':'color',
                    'title': title5
                }
            )
        )
    )
    story.add_slide(slide5_1)


    pop6 = df[(df['Generation'] == generation)]['Population'].sum()
    title6 = f"You Belong to the {format_population(pop6)} {generation}s Worldwide"

    slide6 = Slide(
        Step(
            Data.filter(f"record['Generation'] == '{generation}'"),
            Config(
                {
                    'label':None,
                    'geometry':'area',
                    'title': title6
                }
            )
        )
    )
    story.add_slide(slide6)

    # Start of slide 7
    generations = ['Baby Boomer', 'Gen X', 'Millennial', 'Gen Z', 'Gen A']
    start_index = generations.index(generation)
    slide7 = Slide()

    if generation == 'Baby Boomer':
        # Include all generations in order, stacking as steps
        for i in range(start_index, len(generations)):
            filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in generations[start_index:i+1]])
            step = Step(
                Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
                Config.stackedBar(
                    {
                        'x': 'Population',
                        'color': 'Generation',
                        'stackedBy': 'Generation',
                        'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                    }
                )
            )
            slide7.add_step(step)
    elif generation == 'Gen A':
        # Include all generations in reverse order, stacking as steps
        for i in range(len(generations) - 1, -1, -1):
            filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in generations[i:]])
            step = Step(
                Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
                Config.stackedBar(
                    {
                        'x': 'Population',
                        'color': 'Generation',
                        'stackedBy': 'Generation',
                        'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                    }
                )
            )
            slide7.add_step(step)
    elif generation == 'Gen Z':
        # Include Gen A, Millennials, and Gen Z in order, then stack the rest in reverse order
        initial_generations = generations[start_index - 1:start_index + 2]
        filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in initial_generations])
        step = Step(
            Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
            Config.stackedBar(
                {
                    'x': 'Population',
                    'color': 'Generation',
                    'stackedBy': 'Generation',
                    'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                }
            )
        )
        slide7.add_step(step)

        included_generations = generations[start_index + 2:] + generations[:start_index - 1][::-1]
        for i in range(len(included_generations)):
            filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in initial_generations + included_generations[:i+1]])
            step = Step(
                Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
                Config.stackedBar(
                    {
                        'x': 'Population',
                        'color': 'Generation',
                        'stackedBy': 'Generation',
                        'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                    }
                )
            )
            slide7.add_step(step)
    elif generation == 'Millennial':
        # First step: Include Millennials stacked with Gen Z and Gen X
        initial_generations = ['Gen Z', 'Gen X', 'Millennial']
        filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in initial_generations])
        step = Step(
            Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
            Config.stackedBar(
                {
                    'x': 'Population',
                    'color': 'Generation',
                    'stackedBy': 'Generation',
                    'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                }
            )
        )
        slide7.add_step(step)

        # Second step: Add Baby Boomers and Gen A
        additional_generations = ['Baby Boomer', 'Gen A']
        filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in initial_generations + additional_generations])
        step = Step(
            Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
            Config.stackedBar(
                {
                    'x': 'Population',
                    'color': 'Generation',
                    'stackedBy': 'Generation',
                    'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                }
            )
        )
        slide7.add_step(step)

        # Add remaining generations (if any) step by step
        included_generations = additional_generations + generations[start_index + 1:] + generations[:start_index - 1][::-1]
        for i in range(len(included_generations) - len(initial_generations)):
            filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in initial_generations + included_generations[:i+1 + len(initial_generations)]])
            step = Step(
                Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
                Config.stackedBar(
                    {
                        'x': 'Population',
                        'color': 'Generation',
                        'stackedBy': 'Generation',
                        'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                    }
                )
            )
            slide7.add_step(step)
    elif generation == 'Gen X':
        # Include Baby Boomers, Gen X, and Millennials together at the start
        initial_generations = ['Baby Boomer', 'Gen X', 'Millennial']
        filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in initial_generations])
        step = Step(
            Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
            Config.stackedBar(
                {
                    'x': 'Population',
                    'color': 'Generation',
                    'stackedBy': 'Generation',
                    'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                }
            )
        )
        slide7.add_step(step)

        # Then add the rest of the generations in reverse order
        included_generations = generations[start_index + 2:] + generations[:start_index - 1][::-1]
        for i in range(len(included_generations)):
            filter_condition = " || ".join([f"record['Generation'] == '{gen}'" for gen in initial_generations + included_generations[:i+1]])
            step = Step(
                Data.filter(f"record['Country'] == '{selected_country}' && ({filter_condition}) && record['Gender'] == '{selected_gender}'"),
                Config.stackedBar(
                    {
                        'x': 'Population',
                        'color': 'Generation',
                        'stackedBy': 'Generation',
                        'title': f"Distribution of {g_type} Born Since 1950 ({abr_country})"
                    }
                )
            )
            slide7.add_step(step)
    story.add_slide(slide7)
    # End of Slide 7

    slide8 = Slide()
    slide8.add_step(
        Step(
            Data.filter(f"record['Subregion'] == '{subregion}' && record['Generation'] && record['Gender'] == '{selected_gender}'"),
            Config.bar(
                {
                    'y': 'Population',
                    'y': 'ISO3_code',
                    'color': 'Country',
                    'title': f"Distribution of All {g_type} Born Since 1950 ({subregion})"
                }
            )
        )
    )
    slide8.add_step(
        Step(
            Data.filter(f"record['Subregion'] == '{subregion}' && record['Generation'] && record['Gender'] == '{selected_gender}'"),
            Config.stackedBar(
                {
                    'x': 'Population',
                    'y': 'ISO3_code',
                    'stackedBy': 'Generation',
                    'color': 'Generation',
                    'title': f"Distribution of All {g_type} Born Since 1950 ({subregion})"
                }
            )
        )
    )
    story.add_slide(slide8)

    slide9 = Slide()
    slide9.add_step(
        Step(
            Data.filter(f"record['Continent'] == '{continent}' && record['Generation'] && record['Gender'] == '{selected_gender}'"),
            Config.bar(
                {
                    'x': 'Population',
                    'y': 'Subregion',
                    'color': 'Country',
                    'title': f"Distribution of All {g_type} Born Since 1950 ({continent})"
                }
            )
        )
    )
    slide9.add_step(
        Step(
            Data.filter(f"record['Continent'] == '{continent}' && record['Generation'] && record['Gender'] == '{selected_gender}'"),
            Config.stackedBar(
                {
                    'x': 'Population',
                    'y': 'Subregion',
                    'stackedBy': 'Generation',
                    'color': 'Generation',
                    'title': f"Distribution of All {g_type} Born Since 1950 ({continent})"
                }
            )
        )
    )
    story.add_slide(slide9) 

    slide10 = Slide()
    slide10.add_step(
        Step(
            Data.filter(f"record['Generation'] && record['Gender'] == '{selected_gender}'"),
            Config.bar(
                {
                    'x': 'Continent',
                    'y': 'Population',
                    'color': 'Generation',
                    'title': f"Distribution of All {g_type} Born Since 1950 Worldwide"
                }
            )
        )
    )
    slide10.add_step(
        Step(
            Data.filter(f"record['Generation'] && record['Gender'] == '{selected_gender}'"),
            Config.stackedBar(
                {
                    'x': 'Continent',
                    'y': 'Population',
                    'stackedBy': 'Generation',
                    'color': 'Generation',
                    'title': f"Distribution of All {g_type} Born Since 1950 Worldwide"
                }
            )
        )
    )
    story.add_slide(slide10)

    slide11 = Slide(
        Step(
            Data.filter(f"record['Generation'] && record['Gender'] == '{selected_gender}'"),
            Config.bubble(
                {
                    'size': 'Population',
                    'geometry': 'circle',
                    'color': 'Generation',
                    'label': 'Generation',
                    'title': f"Distribution of All {selected_gender}s Born Since 1950 Worldwide"
                }
            )
        )
    )
    story.add_slide(slide11)

    # Switch on the tooltip that appears when the user hovers the mouse over a chart element.
    story.set_feature('tooltip', True)

    html(story._repr_html_(), width=width, height=height)

    st.download_button('Download HTML export', story.to_html(), file_name=f'demographics-{selected_country}.html', mime='text/html')

    # Close the centered div
    st.markdown('</div>', unsafe_allow_html=True)
