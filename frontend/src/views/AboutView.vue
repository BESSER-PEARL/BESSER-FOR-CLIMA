<template>
  <div class="about-container">
    <h1>About Climaborough City Platform</h1>

    <section class="about-section">
      <h2>Our Mission</h2>
      <p>
        The Climaborough City Platform serves as a comprehensive knowledge centre, 
        providing a common digital space for cities in their climate and digital transition journey. 
        Developed by the Luxembourg Institute of Science and Technology (LIST) in cooperation with 
        DATEN-KOMPETENZZENTRUM STÄDTE UND REGIONEN (DKSR), our platform is part of the CLIMABOROUGH 
        research project within the Horizon Europe framework.
      </p>
    </section>

    <section class="about-section">
      <h2>What We Offer</h2>
      <div class="features-grid">
        <div class="feature-card">
          <h3>Data Integration</h3>
          <p>Access to comprehensive urban data and analytics tools for climate-related decision making.</p>
        </div>
        <div class="feature-card">
          <h3>Climate Solutions</h3>
          <p>Tools and resources to support cities in their transition towards climate neutrality.</p>
        </div>
        <div class="feature-card">
          <h3>Collaboration</h3>
          <p>A shared space for cities to learn from each other and implement best practices.</p>
        </div>
        <div class="feature-card">
          <h3>Innovation</h3>
          <p>Access to cutting-edge research and innovative solutions for urban climate challenges.</p>
        </div>
      </div>
    </section>

    <section class="about-section">
      <h2>Our Partners</h2>
      <div class="partners">
        <div class="partner">
          <h3>LIST</h3>
          <p>Luxembourg Institute of Science and Technology - Lead Developer</p>
        </div>
        <div class="partner">
          <h3>DKSR</h3>
          <p>DATEN-KOMPETENZZENTRUM STÄDTE UND REGIONEN - Technical Partner</p>
        </div>
      </div>
    </section>

    <section class="about-section">
      <h2>Project Background</h2>
      <p>
        The Climaborough project, "Building Green and Climate Neutral City-Hubs," 
        is an initiative under Horizon Europe aimed at accelerating the transition 
        of European cities towards climate neutrality. Our platform serves as a 
        central tool in this mission, providing cities with the digital infrastructure 
        needed to implement and monitor their climate action plans.
      </p>
    </section>

    <section class="about-section">
      <h2>Contact Us</h2>
      <p>
        For more information about the Climaborough City Platform, please contact us at:
      </p>
      <div class="contact-info">
        <p>Email: contact@climaborough.eu</p>
        <p>Address: Luxembourg Institute of Science and Technology</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  color: #333;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.about-section {
  margin-bottom: 3rem;
}

h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.feature-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.feature-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.partners {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.partner {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.partner h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.contact-info {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .about-container {
    padding: 1rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .partners {
    grid-template-columns: 1fr;
  }
}
</style>
