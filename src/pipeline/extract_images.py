import fitz
import os
import json


class ExtractImages:

    def __init__(self, pdf_path, output_dir) -> None:
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.metadata = []

        # Create output directory if it doesn't exist
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception as e:
            raise OSError(f"Failed to create a local dir : {e}")



    def extract_img(self, pdf_path):

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF File not found")

        doc = fitz.open(pdf_path)
        

        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()

            if image_list:
                print(f"Found images")
            else:
                print(f"Not found any images")

            for image_index, img in enumerate(image_list, start=1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                filename = f"page_{page_num + 1}_img_{image_index}.{image_ext}"
                filepath = os.path.join(self.output_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(image_bytes)

                bbox = page.get_image_bbox(img)

                self.metadata.append(
                    {
                        "filepath": filepath,
                        "page_num": page_num + 1,
                        "bbox": {
                            "x0": bbox.x0,
                            "y0": bbox.y0,
                            "x1": bbox.x1,
                            "y1": bbox.y1,
                        },
                    }
                )
        doc.close()
        return self.metadata

    def save_metadata(self, output_path):
        with open(output_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)


if __name__ == "__main__":
    pdf_path = "input.pdf"
    output_dir = "output_dir"


 
