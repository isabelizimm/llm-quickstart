from shiny import reactive
from shiny.express import input, ui, render 
import matplotlib.pyplot as plt
from chatlas import ChatAnthropic, ChatOpenAI, content_image_file

prompt = """
        Analyze this image and generate Python code that creates a matplotlib plot related to the image content. 
        Only use matplotlib.pyplot and numpy. 
        The code should be complete and runnable. 
        Only respond with plaintext Python code, nothing else. 
        Do not include markdown formatting or explanation. 
        Do not include preceding python.
        Start with importing libraries.
        You do not need to recreate the image exactly.
        Instead, mimic the image if possible.
        Do not include fig, ax = plt.subplots(). 
        Do not show the plot.

        Here is an example of what to return:
        import numpy as np                                                                                
        import matplotlib.pyplot as plt                                                                   
        from matplotlib.patches import RegularPolygon                                                         
        colors = ['blue', 'green', 'yellow', 'red']                                                       
        n = 5  # number of rows and columns                                                               
                                                                                                        
        for i in range(n):                                                                                
            for j in range(n):                                                                            
                x = i * 2                                                                                 
                y = j * 2                                                                                 
                color = colors[(i + j) % 4]                                                               
                hexagon = RegularPolygon((x, y), numVertices=4, radius=1, orientation=np.pi/4, color=colo 
                ax.add_patch(hexagon)                                                                     
                                                                                                        
        ax.set_xlim(-1, n * 2 - 1)                                                                        
        ax.set_ylim(-1, n * 2 - 1)                                                                        
        ax.set_aspect('equal')                                                                            
        ax.axis('off') 
        """

code_content = reactive.value("")

with ui.card():
    ui.card_header("Image Analysis App")
    ui.input_radio_buttons(
        "radio",
        "Choose a model:",
        {"1": "gpt-4o", "2": "claude-3-5-sonnet"},
    )
    ui.input_file("file", "Upload an image", accept=[".jpg", ".jpeg", ".png"])
    ui.input_text_area("code_display", "Generated Code:", value="", rows=10)

@render.plot
@reactive.event(input.file)
def generated_plot():
    if not input.file():
        return "Please upload an image"

    if input.radio == 'anthropic':
        chat = ChatAnthropic(model="claude-3-5-sonnet-latest", system_prompt=prompt)
    else:
        chat = ChatOpenAI(model="gpt-4o", system_prompt=prompt)

    file_content = input.file()[0]["datapath"]
    response = chat.chat(content_image_file(file_content))
    
    content = response.content
    if response.content.startswith('```python'):
        content = response.content[10:-3]
    
    # Update the text area with the code
    import re
    import_lines = re.findall(r"^import .+|^from .+ import .+", content, re.MULTILINE)

    # Find the last import line
    if import_lines:
        last_import = import_lines[-1]
        code = content.replace(last_import, last_import + "\n\nfig, ax = plt.subplots()\n")

    ui.update_text_area("code_display", value=code)
    
    fig, ax = plt.subplots()
    exec(str(content))
    return fig