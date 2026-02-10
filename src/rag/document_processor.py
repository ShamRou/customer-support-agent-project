"""Document processing utilities for RAG"""
import os
import re
from typing import List, Dict
from pathlib import Path


class Document:
    """Represents a document chunk"""

    def __init__(self, content: str, metadata: Dict[str, any]):
        import hashlib
        self.content = content
        self.metadata = metadata
        # Create unique ID using source + chunk_id + content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        self.id = f"{metadata['source']}_{metadata.get('chunk_id', 0)}_{content_hash}"


class DocumentProcessor:
    """Process markdown documents for RAG"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document processor

        Args:
            chunk_size: Target size for each chunk (in characters)
            chunk_overlap: Overlap between chunks (in characters)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_markdown_file(self, file_path: str) -> str:
        """Load markdown file content"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_title(self, content: str) -> str:
        """Extract title from markdown (first # heading)"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else "Untitled"

    def split_by_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Split markdown into sections based on headers

        Returns:
            List of dicts with 'title' and 'content'
        """
        # Split by ## headers (keeping the header with its content)
        sections = []
        current_section = {"title": "", "content": ""}

        for line in content.split('\n'):
            # Check if it's a header
            if line.startswith('##'):
                # Save previous section if it has content
                if current_section["content"].strip():
                    sections.append(current_section)

                # Start new section
                title = line.lstrip('#').strip()
                current_section = {"title": title, "content": line + '\n'}
            else:
                current_section["content"] += line + '\n'

        # Add the last section
        if current_section["content"].strip():
            sections.append(current_section)

        return sections

    def chunk_text(self, text: str, metadata: Dict[str, any]) -> List[Document]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of Document objects
        """
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            # Get chunk
            end = start + self.chunk_size
            chunk_text = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n\n')

                break_point = max(last_period, last_newline)
                if break_point > self.chunk_size * 0.5:  # Only if we're not cutting too much
                    chunk_text = chunk_text[:break_point + 1]
                    end = start + break_point + 1

            # Create document
            chunk_metadata = {
                **metadata,
                "chunk_id": chunk_id,
                "chunk_start": start,
                "chunk_end": end
            }

            chunks.append(Document(chunk_text.strip(), chunk_metadata))

            # Move start position with overlap
            start = end - self.chunk_overlap
            chunk_id += 1

        return chunks

    def process_file(self, file_path: str) -> List[Document]:
        """
        Process a markdown file into documents

        Args:
            file_path: Path to markdown file

        Returns:
            List of Document objects
        """
        # Load content
        content = self.load_markdown_file(file_path)

        # Extract metadata
        title = self.extract_title(content)
        file_name = Path(file_path).name

        # Split into sections
        sections = self.split_by_sections(content)

        # Process each section
        all_documents = []

        for section in sections:
            metadata = {
                "source": file_name,
                "title": title,
                "section": section["title"],
                "file_path": file_path
            }

            # Chunk the section
            chunks = self.chunk_text(section["content"], metadata)
            all_documents.extend(chunks)

        return all_documents

    def process_directory(self, directory_path: str, pattern: str = "*.md") -> List[Document]:
        """
        Process all markdown files in a directory

        Args:
            directory_path: Path to directory
            pattern: File pattern to match

        Returns:
            List of all Document objects
        """
        all_documents = []
        directory = Path(directory_path)

        # Find all matching files
        files = sorted(directory.glob(pattern))

        print(f"Found {len(files)} markdown files")

        for file_path in files:
            print(f"\nProcessing: {file_path.name}")
            documents = self.process_file(str(file_path))
            print(f"  Created {len(documents)} chunks")
            all_documents.extend(documents)

        print(f"\nTotal documents: {len(all_documents)}")
        return all_documents


def clean_text(text: str) -> str:
    """Clean text for better embedding quality"""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    # Remove markdown artifacts that don't add semantic value
    text = re.sub(r'```\w*\n', '```\n', text)  # Remove language specifiers from code blocks

    # Normalize line endings
    text = text.replace('\r\n', '\n')

    return text.strip()
