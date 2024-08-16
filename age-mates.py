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

# Add a column that marks whether the row matches all the selected criteria
df['MatchCriteria'] = df.apply(lambda row: 'yes' if (row['Country'] == selected_country and row['Gender'] == selected_gender) else 'no', axis=1)

# Sort the DataFrame so that:
# 1. Rows matching all criteria are at the top.
# 2. Rows within each generation are sorted by year in ascending order.
df = df.sort_values(by=['MatchCriteria', 'Year'], ascending=[False, True])

# Drop the MatchCriteria column since it's no longer needed after sorting
df = df.drop(columns=['MatchCriteria'])

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

    # Set a handler that prevents showing specific elements

    label_handler_method = (
        "if(event.detail.text.split(',')[1] < 1000) event.preventDefault()"
    )
    story.add_event("plot-marker-label-draw", label_handler_method)

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
    if selected_gender == 'Male':
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
                        'colorPalette': '#4171CDFF',
                        'label' :{ 
                            'format' : 'dimensionsFirst',
                            'fontSize' : '2.5em',
                            },
                        }},
                })
            )
        )
        story.add_slide(slide1)
    else:
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
                        'colorPalette': '#FE34AE',
                        'label' :{ 
                            'format' : 'dimensionsFirst',
                            'fontSize' : '2.5em',
                            },
                        }},
                })
            )
        )
        story.add_slide(slide1)

    pop2 = df[(df['Year'] == selected_year) & (df['Country'] == selected_country)]['Population'].sum()
    title2 = f"You Are One of {format_population(pop2)} People Born in {selected_year} in {abr_country}"

    if selected_gender == 'Male':
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
                            'colorPalette': '#4171CDFF #FE34AE',
                            'label' :{ 
                            'format': 'measureFirst',
                            'fontSize' : '1.8em',
                            }
                        }},
                })
            )
        )
        story.add_slide(slide2)
    else:
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
                            'colorPalette': '#FE34AE #4171CDFF',
                            'label' :{ 
                                'format': 'measureFirst',
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
                    'colorPalette': '#1f4691 #03AE71FF #F4941BFF #F4C204FF #D49664FF #F25456FF #9E67ABFF #BCA604FF #846E1CFF #FC763CFF #B462ACFF #F492FCFF #BC4A94FF #9C7EF4FF #9C52B4FF #6CA2FCFF #5C6EBCFF #7C868CFF #AC968CFF #4C7450FF #AC7A4CFF #7CAE54FF #4C7450FF #9C1A6CFF #AC3E94FF #B41204FF',
                    "label": {
                        'format': 'dimensionsFirst',
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

    if selected_year == 1950:
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
                        'color': 'Generation'
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'colorPalette': '#1f4691',
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
        slide6.add_step(
            Step(
                Config(
                    {
                        'x': ['Year2', 'IsSelectedYear'],
                        'label': 'Population',
                        'lightness': 'IsSelectedYear'
                        
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'minLightness': 0,
                        'maxLightness': 0.4
                    },
                }
                })
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

    elif selected_year != 1950:
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
                        'color': 'Generation'
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'colorPalette': '#1f4691',
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
        slide6.add_step(
            Step(
                Config(
                    {
                        'x': ['Year2', 'IsSelectedYear'],
                        'label': 'Population',
                        'lightness': 'IsSelectedYear'
                        
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'minLightness': 0.4,
                        'maxLightness': 0
                    },
                }
                })
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
                    'color': 'Generation',
                    'lightness': None
                }
            ),
            Style({
                    "plot": {
                    "marker": {
                        'colorPalette': '#1f4691',
                        'minLightness': 0,
                        'maxLightness': 0
                    },
                }
                })
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
    
    if generation == 'Baby Boomer':
        slide7.add_step(
            Step(
                Data.filter(None),
                Config(
                    {
                        'label':['Generation','Population'],
                        'title': f"Your Generation is {(pop6 / pop7) * 100:.1f}% of People Born after 1950",
                        'color': 'Generation'
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'colorPalette': '#1f4691 #03AE71FF #F4941BFF #F4C204FF #D49664FF',
                    },
                }
                })
            )
        )
    if generation == 'Gen X':
        slide7.add_step(
            Step(
                Data.filter(None),
                Config(
                    {
                        'label':['Generation','Population'],
                        'title': f"Your Generation is {(pop6 / pop7) * 100:.1f}% of People Born after 1950",
                        'color': 'Generation'
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'colorPalette': '#03AE71FF #1f4691 #F4941BFF #F4C204FF #D49664FF',
                    },
                }
                })
            )
        )
    if generation == 'Millennial':
        slide7.add_step(
            Step(
                Data.filter(None),
                Config(
                    {
                        'label':['Generation','Population'],
                        'title': f"Your Generation is {(pop6 / pop7) * 100:.1f}% of People Born after 1950",
                        'color': 'Generation'
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'colorPalette': '#03AE71FF #F4941BFF #1f4691 #F4C204FF #D49664FF',
                    },
                }
                })
            )
        )
    if generation == 'Gen Z':
        slide7.add_step(
            Step(
                Data.filter(None),
                Config(
                    {
                        'label':['Generation','Population'],
                        'title': f"Your Generation is {(pop6 / pop7) * 100:.1f}% of People Born after 1950",
                        'color': 'Generation'
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'colorPalette': '#03AE71FF #F4941BFF #F4C204FF #1f4691 #D49664FF',
                    },
                }
                })
            )
        )
    if generation == 'Gen A':
        slide7.add_step(
            Step(
                Data.filter(None),
                Config(
                    {
                        'label':['Generation','Population'],
                        'title': f"Your Generation is {(pop6 / pop7) * 100:.1f}% of People Born after 1950",
                        'color': 'Generation'
                    }
                ),
                Style({
                    "plot": {
                    "marker": {
                        'colorPalette': '#03AE71FF #F4941BFF #F4C204FF #D49664FF #1f4691',
                    },
                }
                })
            )
        )
    story.add_slide(slide7)

    slide8 = Slide()
    if selected_year == 1950:
        slide8.add_step(
            Step(
                    Data.filter(None),
                    Config(
                        {
                            'label':None,
                            'x':['Year2','Generation','Population', 'IsSelectedYear'],
                            'color': 'Generation',
                            'lightness': 'IsSelectedYear',
                            'title': f"You and Your {format_population(pop5)} Age-Mates Are {(pop5 / pop7) * 100:.1f}% of People Born after 1950",
                        }
                    ),
                    Style({
                        "plot": {
                        "marker": {
                            'minLightness': 0,
                            'maxLightness': 0.4
                        },
                    }
                    })

            )
        )
    elif selected_year != 1950:
        slide8.add_step(
            Step(
                    Data.filter(None),
                    Config(
                        {
                            'label':None,
                            'x':['Year2','Generation','Population', 'IsSelectedYear'],
                            'color': 'Generation',
                            'lightness': 'IsSelectedYear',
                            'title': f"You and Your {format_population(pop5)} Age-Mates Are {(pop5 / pop7) * 100:.1f}% of People Born after 1950",
                        }
                    ),
                    Style({
                        "plot": {
                        "marker": {
                            'minLightness': 0.4,
                            'maxLightness': 0
                        },
                    }
                    })

            )
        )
    story.add_slide(slide8)

    handler = """
    if (window.storyCurrentSlide !== undefined && window.storyBgImages[window.storyCurrentSlide]) {
        event.renderingContext.drawImage(window.storyBgImages[window.storyCurrentSlide], 0, 0,
            event.detail.rect.size.x, event.detail.rect.size.y);
        event.preventDefault();
    }
    """
    story.add_event("background-draw", handler)

    update_event_html = """
    <div><script type="module">
    function loadImage(url) {
        return new Promise((resolve) => {
        const image = new Image();
        image.addEventListener('load', () => { resolve(image); });
        image.src = url;
        })
    }

    const vp = document.querySelector("vizzu-player");

    Promise.all([
        vp.initializing,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        loadImage('https://raw.githubusercontent.com/vizzu-streamlit/age-mates/main/66a7736d61b51207bfff94e2_Vizzu-Team-Staircase-v2.webp')   
    ]).then(values => {
        const [chart, ...images] = values;
        window.storyBgImages = images;
        vp.addEventListener('update', (e) => {
        window.storyCurrentSlide = e.detail.currentSlide;
        chart.feature.rendering.update();
        });
        chart.feature.rendering.update();
    })
    </script></div>
    """
    
    # Switch on the tooltip that appears when the user hovers the mouse over a chart element.
    story.set_feature('tooltip', True)

    html(story._repr_html_() + update_event_html, width=width, height=height)

    st.download_button('Download HTML export', story.to_html() + update_event_html, file_name=f'demographics-{selected_country}.html', mime='text/html')

    # Close the centered div
    st.markdown('</div>', unsafe_allow_html=True)
