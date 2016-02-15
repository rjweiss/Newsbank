# Newsbank code

This repository contains data management and analysis scripts for working with the newsbank data.

## Data management

Parsing is handled by the script `parse.py`. The process is currently the following:

1. Iterate through the data directory, walking through the directory structure
2. Open files found
3. Parse xml document into an etree object
4. Directly access relevant XML fields via XPath
5. Dump fields into dictionary and return the dictionary

There is also minimal processing of the text itself:
1. Cues and names are denoted with fully capitalized strings.  These are counted separately and returned in the maintext dictionary.

The document structure is returned as follows
```json
{
  'paper': \* Title of program 
  'date': \* Date of broadcast
  'show': \* Alternate title?
  'locations': \* Locations in program?
  'indexterms': \* Newsbank's categorization
  'maintext':
    {
      'names': \* All found names, meaning all capitalized text in the transcript
      'text': \* Raw transcript concatenated as a single string
    }
}
```

Currently this script does not write any results anywhere.  
