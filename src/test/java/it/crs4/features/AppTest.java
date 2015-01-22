package it.crs4.features;

import java.io.File;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

import loci.formats.FormatTools;
import loci.formats.MetadataTools;
import loci.formats.IFormatWriter;
import loci.formats.ImageWriter;
import loci.formats.meta.IMetadata;
import loci.common.services.ServiceFactory;
import loci.formats.services.OMEXMLService;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class AppTest extends TestCase {

  private static final Logger LOGGER = LoggerFactory.getLogger(App.class);

  private int pixelType = FormatTools.UINT16;
  private int seriesCount = 2;
  private int w = 512;
  private int h = 512;
  private int c = 1;
  private int z = 5;
  private int t = 2;

  private int size = w * h * c * FormatTools.getBytesPerPixel(pixelType);
  private int planesCount = z * t;

  private byte[][][] data;


  private byte[] makeImg() {
    byte[] img = new byte[size];
    for (int i = 0; i < img.length; i++) {
      img[i] = (byte) (256 * Math.random());
    }
    return img;
  }

  private String makeImgFile() throws Exception {
    File target = File.createTempFile("pydoop_features_", ".ome.tiff");
    String id = target.getAbsolutePath();
    String ptString = FormatTools.getPixelTypeString(pixelType);
    ServiceFactory factory = new ServiceFactory();
    OMEXMLService service = factory.getInstance(OMEXMLService.class);
    IMetadata meta = service.createOMEXMLMetadata();
    for (int s = 0; s < seriesCount; s++) {
      MetadataTools.populateMetadata(meta, s, null, false, "XYZCT",
        ptString, w, h, z, c, t, c);
    }
    IFormatWriter writer = new ImageWriter();
    writer.setMetadataRetrieve(meta);
    writer.setId(id);
    data = new byte[seriesCount][planesCount][size];
    for (int s = 0; s < seriesCount; s++) {
      writer.setSeries(s);
      for (int p = 0; p < z*t; p++) {
        byte[] img = makeImg();
        writer.saveBytes(p, img);
        data[s][p] = img;
      }
    }
    writer.close();
    return id;
  }

  public AppTest(String testName) {
    super(testName);
  }

  public static Test suite() {
    return new TestSuite(AppTest.class);
  }

  public void testApp() throws Exception {
    assertTrue(true);  // FIXME
    String fn = makeImgFile();
    LOGGER.info("Created {}", fn);
  }

}
